import argparse
import googlemaps
import pandas as pd
import random

ROUND_DISTANCE_TIME = 1440   # unit is mins so a day=1440


class VentilatorDist():
    def __init__(self, vent_data_file, location_map, round_distance_time=ROUND_DISTANCE_TIME):
        self.vent_data_file = vent_data_file
        self.location_map = location_map
        self.round_distance_time = round_distance_time

    def _amount_to_transfer(self, need, avail):
        ''' '''
        if need > avail:
            return avail
        else:
            return need
    
    def _transfer_amount(self, df, dist, source, dest, amount):
        ''' '''
        df.at[source, 'vent_avail'] = df.at[source, 'vent_avail'] - amount
        df.at[dest, 'vent_need'] = df.at[dest, 'vent_need'] - amount
        dist['->'.join([source, dest])] = amount
        #print('transfering: {} -> {} - {}'.format(source, dest, amount))

    def _print_results(self, dist, df):
        """ """
        print('\n----- Completed -----')
        print('\nSuggested Distribution\n')
        for k,v in dist.items():
            print('    {} {}'.format(k,v))
        print('\nResulting Table (and remaining need)')
        print(df)
        print('-------------')

    def run(self):
        # read in vent data 
        df_t = pd.read_csv(self.vent_data_file, sep=',')

        # create new df with cols for every location
        all_locs = list(df_t.loc[ : , 'location'])
        d = {
            'location': all_locs,
            'vent_avail': list(df_t.loc[ : , 'vent_avail']),
            'vent_need': list(df_t.loc[ : , 'vent_need']),
        }
        for l in df_t.loc[ : , 'location']:
            d[l] = [None] * len(all_locs)
        
        df = pd.DataFrame(data=d)
        df.set_index('location', inplace=True, drop=True)
    
        # add distance from one location to another for every location in df
        locs = df.index.values   # get static list, has issues otherwise
        for loc in locs:
            for loc1 in locs:
                dist = self.location_map.get_distance(loc, loc1)
                if ROUND_DISTANCE_TIME:
                    dist = round(dist/ROUND_DISTANCE_TIME)
                df.at[loc, loc1] =  dist
                #print('---dist from {} to {} is {}'.format(loc, loc1, dist))
        
        print('\nCurrent Ventilator Need:\n {}'.format(df))
        print('---------')
    
        dist = {}
        
        # first account for locations fulfilling their own need with their own stock supply
        for loc, row in df.iterrows():
            if row['vent_need'] > 0 and row['vent_avail'] > 0:
                amount = self._amount_to_transfer(row['vent_need'], row['vent_avail'])
                self._transfer_amount(df, dist, loc, loc, amount)

        # now distribute rest of free ventilators, prioritizing locations that are close
        for d in [0,1,2,3]:
            for loc, row in df.iterrows():
                if row['vent_avail'] > 0:
                    loc_at_dist = row.drop(['vent_avail', 'vent_need'])
                    loc_at_dist = list(loc_at_dist.where(loc_at_dist == d).index)
                    random.shuffle(loc_at_dist)   # fairness - when looking to share with each locale at same distance away, randomly shuffle order
                    for dest_loc in loc_at_dist:
                        if df.at[loc, 'vent_avail'] > 0 and df.at[dest_loc, 'vent_need'] > 0:
                            amount = self._amount_to_transfer(df.at[dest_loc, 'vent_need'], df.at[loc, 'vent_avail'])
                            self._transfer_amount(df, dist, loc, dest_loc, amount)
        
        self._print_results(dist, df)
import argparse
import googlemaps
import pandas as pd
import random
from covid import LocationMap



def amount_to_transfer(need, avail):
    ''' '''
    if need > avail:
        return avail
    else:
        return need


def transfer_amount(df, dist, source, dest, amount):
    ''' '''
    df.at[source, 'vent_avail'] = df.at[source, 'vent_avail'] - amount
    df.at[dest, 'vent_need'] = df.at[dest, 'vent_need'] - amount
    dist[':'.join([source, dest])] = amount
    print("transfering: {} -> {} - {}".format(source, dest, amount))


def main():
    ''' '''
    parser = argparse.ArgumentParser(description='do things')
    parser.add_argument('-k', '--key', dest='google_key', help='google key')
    parser.add_argument('-v', dest='vent_data_file' )
    args = parser.parse_args()

    # load google map
    #gmaps = googlemaps.Client(key=args.google_key)
    #lm = LocationMap(gmaps=gmaps)

    # read in vent data 
    df_t = pd.read_csv(args.vent_data_file, sep=',')

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
    for loc, row in df.iterrows():
        for loc1, row1 in df.iterrows():
            #df.at[df.at[loc, loc]] = round(lm.get_distance(loc, loc1) / (60*24))   # round distance times to days
            df.at[loc, loc1] = 1
    
    print('Data ready for transfer processing:\n {}'.format(df))
    print('---------')
  
    dist = {}
    
    # first account for locations fulfilling their own need with their own stock supply
    for loc, row in df.iterrows():
        if row['vent_need'] > 0 and row['vent_avail'] > 0:
            amount = amount_to_transfer(row['vent_need'], row['vent_avail'])
            transfer_amount(df, dist, loc, loc, amount)

    print('after trying to fulfull from own supply: \n {} \n {}'.format(dist, df))
    print('---------')

    # now distribute rest of free ventilators, prioritizing locations that are close
    total_free_vents = sum(df['vent_avail'])
    total_need_vents = sum(df['vent_need'])
    for d in [0,1,2,3]:
        for loc, row in df.iterrows():
            if row['vent_avail'] > 0:
                loc_at_dist = row.drop(['vent_avail', 'vent_need'])
                loc_at_dist = list(loc_at_dist.where(loc_at_dist == d).index)
                random.shuffle(loc_at_dist)   # fairness - when looking to share with each locale at same distance away, randomly shuffle order
                for dest_loc in loc_at_dist:
                    if df.at[loc, 'vent_avail'] > 0 and df.at[dest_loc, 'vent_need'] > 0:
                        amount = amount_to_transfer(df.at[dest_loc, 'vent_need'], df.at[loc, 'vent_avail'])
                        transfer_amount(df, dist, loc, dest_loc, amount)
    
    print('Completed distribution and table: {}\n {}\n'.format(dist, df))
    print('-------------')

if __name__ == '__main__':
    main()
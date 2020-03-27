import argparse
import googlemaps
import pandas as pd
import random
from covid import LocationMap



def transfer_vent_amount(need, avail):
    ''' '''
    if need > avail:
        return avail
    else:
        return need

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
    print(df_t)

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

    # add distance from one location to another for every location in df
    for idx, row in df.iterrows():
        for idx1, row1 in df.iterrows():
            #df.at[df.at[idx1, 'location']] = round(lm.get_distance(row['location'], row1['location']) / (60*24))   # round distance times to days
            df.at[idx, df.at[idx1, 'location']] = 1
    
    print('Data ready for transfer processing:\n {}'.format(df))
    print('---------')

    dist = {}
    
    # first account for locations fulfilling their own need with their own stock supply
    for idx, row in df.iterrows():
        if row['vent_need'] > 0 and row['vent_avail'] > 0:
            vent_transfer = transfer_vent_amount(row['vent_need'], row['vent_avail'])
            dist[':'.join([row['location'], row['location']])] = vent_transfer
            df.at[idx, 'vent_need'] = row['vent_need'] - vent_transfer
            df.at[idx, 'vent_avail'] = row['vent_avail'] - vent_transfer

    print('after using own stocks: \n {} \n {}'.format(dist, df))
    print('---------')
    
    # now distribute rest of free ventilators, prioritizing locations that are close
    total_free_vents = sum(df['vent_avail'])
    total_need_vents = sum(df['vent_need'])
    for d in [0,1,2,3]:
        for idx, row in df.iterrows():
            if row['vent_avail'] > 0:
                loc_at_dist = row.drop(['location', 'vent_avail', 'vent_need',])
                loc_at_dist = list(loc_at_dist.where(loc_at_dist == d).index)
                random.shuffle(loc_at_dist)   # fairness - when looking to share with each locale at same distance away, randomly shuffle order
                for loc in loc_at_dist:
                    loc_row = df[loc]
                    if row["vent_avail"] > 0 and loc_row['vent_need'] > 0:
                        transfer = transfer_vent_amount(
                            loc_row['vent_need'], row['vent_avail']
                        )
        
    


if __name__ == '__main__':
    main()
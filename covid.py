import argparse
import csv
import requests
from io import StringIO

from datetime import datetime, timedelta

import googlemaps


class LocationMap:
    def __init__(self, gmaps):
        self.gmaps = gmaps

    def get_travel_time(self, origin, destination, mode="driving"):
        directions_result = self.gmaps.directions(origin=origin,
                                             destination=destination,
                                             mode=mode)
        # get primary option
        try:
            legs = directions_result[0]['legs']
        except:
            return 0
        seconds = sum([x['duration']['value'] for x in legs])
        minutes = seconds / 60.0
        return minutes

    def get_distance(self, source_location, target_location):
        return round(self.get_travel_time(source_location, target_location))

    def get_locations(self, query):
        output = self.gmaps.places(query)
        results = []
        for result in output.get('results', []):
            if 'hospital' in result.get('types', []):
                results.append(dict(
                    id=result['id'],
                    name=result['name'],
                    formatted_address=result['formatted_address'],
                    lat=result['geometry']['location']['lat'],
                    lng=result['geometry']['location']['lng'],
                ))
        return results


def load_csv(file):
    """ load csv as list of dictionaries"""
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        return [dict(row) for row in reader]


def load_zip_code_data():
    """
    :return:
    """
    results = []
    with open('data/uszips.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['fips'] = row.pop('county_fips')
            results.append(dict(row))
    return results


def load_icu_beds():
    results = []
    with open('data/khn_icu_beds.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['fips'] = row.pop('cnty_fips')
            results.append(dict(row))
    return results


def load_covid_cases_data(date=None):
    """
    03-22-2020 first date to include FIPS
    :date: mm-dd-yyyy
    :return:
        {'Active': '0',
      'Admin2': 'Abbeville',
      'Combined_Key': 'Abbeville, South Carolina, US',
      'Confirmed': '3',
      'Country_Region': 'US',
      'Deaths': '0',
      'Last_Update': '2020-03-26 23:48:35',
      'Lat': '34.22333378',
      'Long_': '-82.46170658',
      'Province_State': 'South Carolina',
      'Recovered': '0',
      'FIPS' '06059'}
    """
    if not date:
        date = datetime.today()
    data = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date.strftime("%m-%d-%Y")}.csv')

    f = StringIO(data.text)
    reader = csv.DictReader(f, delimiter=',')
    results = {}
    for row in reader:
        fips = row.pop('FIPS', None)
        if fips:
            results[int(fips)] = row
    print(f"{date.strftime('%m-%d-%Y')} has {len(results.keys())} results")
    return results


def load_covid_cases_data_all():
    """
    data starts at 01-22-2020
     {date:
        fip: {data}
     }
    :return:
    """
    covid_data = dict()
    date = datetime.strptime('03-23-2020', '%m-%d-%Y')  # first date johns hopkins included county data
    today = datetime.today()
    while date <= today:
        covid_data[date.strftime('%m-%d-%Y')] = load_covid_cases_data(date)
        date = date + timedelta(days=1)
    return covid_data


def predicted_active_covid_case_count(date, county, covid_data_all=None):
    """
    simple prediction of covid cases for a county and date
    if data is known, actual will be returned
    :param date:
    :param county:
    :return:
    """
    if not covid_data_all:
        covid_data_all = load_covid_cases_data_all()
    predict_date = datetime.strptime(date, '%m-%d-%Y')

    # if a past date, give the known number
    if predict_date.strftime('%m-%d-%Y') in covid_data_all:
        print('it\'s in here')
        return covid_data_all[predict_date.strftime('%m-%d-%Y')].get(county, {}).get('Active', None)

    # max prediction is 5 days out
    if (predict_date - datetime.today()).days > 5:
        print('no idea')
        return

    t_minus_03 = predict_date - timedelta(days=3)
    t_minus_01 = predict_date - timedelta(days=1)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='do things')
    parser.add_argument('-k', '--key', dest='google_key', help='google key')
    args = parser.parse_args()

    zip_code_data = load_zip_code_data()
    icu_beds_data = load_icu_beds()

    print(predicted_active_covid_case_count(date='03-26-2020', county=45001))
    covid_cases_data = load_covid_cases_data()

    gmaps = googlemaps.Client(key=args.google_key)
    lm = LocationMap(gmaps=gmaps)

    from pprint import pprint
    locations = lm.get_locations(query='illinois hospitals')  # hospitals
    for location in locations:
        print(f"{location['name']} is {round(lm.get_travel_time('Ohare airport', location['formatted_address']))} mins from Ohare")



import argparse
import csv
import requests
from io import StringIO

from datetime import datetime

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


def load_zip_code_data():
    """

    :return:
    """
    with open('data/uszips.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [dict(row) for row in reader]


def load_covid_cases_data():
    """
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
      'FIPS' '06059}
    """
    today = datetime.today().strftime('%m-%d-%Y')
    data = requests.get(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{today}.csv')

    f = StringIO(data.text)
    reader = csv.DictReader(f, delimiter=',')
    return [dict(row) for row in reader]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='do things')
    parser.add_argument('-k', '--key', dest='google_key', help='google key')
    args = parser.parse_args()

    zip_code_data = load_zip_code_data()
    covid_cases = load_covid_cases_data()

    gmaps = googlemaps.Client(key=args.google_key)
    lm = LocationMap(gmaps=gmaps)

    from pprint import pprint
    locations = lm.get_locations(query='illinois hospitals')  # hospitals
    for location in locations:
        print(f"{location['name']} is {round(lm.get_travel_time('Ohare airport', location['formatted_address']))} mins from Ohare")



import argparse

import googlemaps


class LocationMap():
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='do things')
    parser.add_argument('-k', '--key', dest='google_key', help='google key')
    args = parser.parse_args()

    gmaps = googlemaps.Client(key=args.google_key)
    lm = LocationMap(gmaps=gmaps)

    from pprint import pprint
    locations = lm.get_locations(query='illinois hospitals')  # hospitals
    for location in locations:
        print(f"{location['name']} is {round(lm.get_travel_time('Ohare airport', location['formatted_address']))} mins from Ohare")

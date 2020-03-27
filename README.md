# COVID

mutually beneficially distribution algorithm that considers the logistical and cleaning transaction costs and the expected ventilator need in an area

## Running
how to get an API key: https://github.com/googlemaps/google-maps-services-python

`python covid.py -k GOOGLE_API_KEY -v <ventilator data file>`

## Functions included
- distance between two places
- word query to address/location (‘hospitals near x’ or ‘hospitals in zipcode’)
- all zip codes data with population
- covid cases mapped to location
- run ventilator distribution algorithm

## Ventilator Distribution Algorithm
The ventilator distribution algorithm follows a simple strategy of attempting to optimize the time the ventilator is in use. It does this by mininizing the amount to time a ventilator is offline due to transportation. At at give time interval, the algorithm will take the following steps to find the near-optimal way of distributing currently available ventilators among all locations that are in need.

  - Load current location and availability of ventilators for next time period. (i.e. "Atlanta has 10 available ventilators")
  - For every location that is in need of ventilators, look first to fill own need with available ventilators at location.
  - Repeat next sub-steps for DAY_COUNT =[1,2,3] (starting with 1) until available ventilator stock is depleted
    - Next, for each location that has available ventilators, get list of locations that are <DAY_COUNT day away and still have unfulfilled ventilator need.
    - randomly shuffle the list of locations (fairness mechanism, location randomly chooses which location to service first, given the list of locations is all the same distance away
  

prioritize the need by distance. So first locations look to see if they have projected need, then fill from their own stocks. Next, for each location look to all locations within distance of 1 day, then attempt to fill that need. Next, look to all locations with distance of 2 day, then attempt to fill need. By doing this, we optimize the amount of time a ventilator is in use versus in transport.

## Data Sources
- us zip codes from: https://simplemaps.com/data/us-zips
- icu beds: https://khn.org/news/as-coronavirus-spreads-widely-millions-of-older-americans-live-in-counties-with-no-icu-beds/
- covid cases: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports

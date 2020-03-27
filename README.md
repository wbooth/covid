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
  
**_Example distribution given 3 locations_**
```
Current Ventilator Need:
               vent_avail  vent_need chicago indianapolis san diego
location                                                          
chicago                5         10       0            0         1
indianapolis          20          5       0            0         1
san diego              0         15       1            1         0
---------

----- Completed -----

Suggested Distribution

    chicago->chicago 5
    indianapolis->indianapolis 5
    indianapolis->chicago 5
    indianapolis->san diego 10

Resulting Table (and remaining need)
              vent_avail  vent_need chicago indianapolis san diego
location                                                          
chicago                0          0       0            0         1
indianapolis           0          0       0            0         1
san diego              0          5       1            1         0
```

## Data Sources
- us zip codes from: https://simplemaps.com/data/us-zips
- icu beds: https://khn.org/news/as-coronavirus-spreads-widely-millions-of-older-americans-live-in-counties-with-no-icu-beds/
- covid cases: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports

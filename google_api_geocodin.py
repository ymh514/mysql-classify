import googlemaps
from datetime import datetime
import json

gmaps = googlemaps.Client(key='')

# # Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((25.050555555555555, 121.37559444444443))
jj = json.dumps(reverse_geocode_result)
data2 = json.loads(jj)
print(data2[4]['formatted_address'])

# # Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)

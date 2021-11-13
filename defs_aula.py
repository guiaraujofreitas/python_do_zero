import time #library to control the time
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent= 'geopiExercise')

def get_longlat (x):
    
    index,row = x
    time.sleep (1)
    
    #chamada api
    response = geolocator.reverse(row['query'])
    address = geolocator.reverse.raw['address']
    
    try:
        place_id= response.raw['place_id'] if 'place_id' in response.raw else 'NA'
        osm_type= response.raw['osm_type'] if 'osm_type' in response.raw else 'NA'
        country= response.raw['address']['country'] if 'country' in response.raw ['address']else 'NA'
        country_code= response.raw['address']['country_code'] if 'country_code' in response.raw['address'] else 'NA'
        
        return place_id,osm_type,country,country_code
    
    except:
           return None, None, None, None


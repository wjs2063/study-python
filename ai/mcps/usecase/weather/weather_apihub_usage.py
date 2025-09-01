import requests
from dotenv import load_dotenv
import os

load_dotenv()

auth_key = os.getenv("DATA_HUB_KEY")
base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
# response = requests.get(url=base_url,
#                         params={"ServiceKey": auth_key, "pageNo": 1, "numOfRows": 1000, "dataType": "JSON", "nx": 55,
#                                 "ny": 127,"base_date":"20250901","base_time":"1200"})
#
# print(response.json())


from geopy.geocoders import Nominatim
import truststore
truststore.inject_into_ssl()
def geocoding(address):
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    geo = geolocoder.geocode(address)
    crd = {"lat": str(geo.latitude), "lng": str(geo.longitude)}

    return crd

crd = geocoding("대구 수성구")
print(crd['lat'])
print(crd['lng'])
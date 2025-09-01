from aiohttp import ClientSession
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("DATA_HUB_KEY")

weather_mcp = FastMCP(name="weather_mcp", host="0.0.0.0", port=8080)

"""
{"ServiceKey": auth_key, "pageNo": 1, "numOfRows": 1000, "dataType": "JSON", "nx": 55,
                                "ny": 127,"base_date":"20250901","base_time":"1200"}
"""

base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"


from geopy.geocoders import Nominatim
import truststore
truststore.inject_into_ssl()
def geocoding(address):
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    geo = geolocoder.geocode(address)
    crd = {"lat": str(geo.latitude), "lng": str(geo.longitude)}

    return crd


@weather_mcp.tool()
async def convert_location_to_coordinate(location:str) -> tuple:
    """
    검색할 지역의 위도/경도를 반환하는 함수입니다.
    Args:
        location:

    Returns:
        tuple 형태의 위도,경도를 반환
        (위도,경도)

    """
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    geo = geolocoder.geocode(location)
    crd = {"lat": str(geo.latitude), "lon": str(geo.longitude)}
    return crd['lat'], crd['lon']


@weather_mcp.tool()
async def get_weather(latitude: int, longitude: int, base_date: str, base_time: str, page_no: int = 1,
                      num_of_rows: int = 1000):
    """
    초단기실황, 초단기예보, 단기((구)동네)예보, 예보버전 정보를 조회하는 서비스입니다. 초단기실황정보는 예보 구역에 대한 대표 AWS 관측값을, 초단기예보는 예보시점부터 6시간까지의 예보를,
    단기예보는 예보기간을 글피까지 확장 및 예보단위를 상세화(3시간→1시간)하여 시공간적으로 세분화한 예보를 제공합니다.
    Args:
        latitude: 위도
        longitude: 경도
        base_date: 20250901 처럼 년(4자리)월(2자리)일(2자리)
        base_time: 24시간 기준으로 4자리 포맷 30분단위, 예시 1800(18시), 0900(09시)
        page_no: 가져올 페이지
        num_of_rows: 가져올 개수

    Returns:

    """
    params = {"ServiceKey": api_key, "pageNo": page_no, "numOfRows": num_of_rows, "dataType": "JSON", "nx": str(latitude),
              "ny": str(longitude), "base_date": base_date, "base_time": base_time}
    print(params)
    async with ClientSession() as session:
        async with session.get(url=base_url, params=params) as response:
            response = await response.json()
            return response

if __name__ == '__main__':
    weather_mcp.run(transport="streamable-http")
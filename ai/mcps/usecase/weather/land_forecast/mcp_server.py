import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from aiohttp import ClientSession,TCPConnector
import os
import truststore
import certifi
import ssl

ssl_ctx = ssl.create_default_context(cafile=certifi.where())

truststore.inject_into_ssl()
load_dotenv()

mcp = FastMCP(name="weather_apihub_mcp",host="0.0.0.0",port=8080)
api_key = os.getenv("OPEN_APIHUB_KEY")

@mcp.tool()
async def get_weather_information(page_no:int,num_of_rows:int,reg_id:str) -> dict:
    """
    한국지역의 육상예보조회API입니다. 기온,강수확률,풍향,풍속,하늘상태,강수상태에 대한 기상정보를 가져올 수 있습니다

    wfCd : 날씨코드 하늘상태
    rnYn : 강수형태
    wf : 날씨
    ta : 예상기온
    wd1 : 풍향
    wd2 : 풍향
    wslt : 풍속 강도코드


    Args:
        page_no:  페이지번호
        num_of_rows: 한 페이지 결과 수
        reg_id: 예보구역코드

    Returns:

    """
    params = {
        "pageNo":page_no,
        "numOfRows":num_of_rows,
        "dataType": "JSON",
        "regId":reg_id,
        "authKey":api_key

    }
    async with ClientSession(connector=TCPConnector(ssl=ssl_ctx)) as session:
        async with session.get(url="https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstMsgService/getLandFcst",params=params) as response:
            response = await response.json()
            print(response)
            return response["response"]["body"]["items"]["item"][0]


# params = {
#     "pageNo":1,
#     "numOfRows":10,
#     "dataType":"JSON",
#     "regId":"11B10101",
#     "authKey":os.getenv("OPEN_APIHUB_KEY")
# }
#
# response = requests.get(url="https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstMsgService/getLandFcst",params=params)
#
# print(response.json())


# response = requests.get(url="https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst?pageNo=1&numOfRows=1000&dataType=JSON&base_date=20250903&base_time=0600&nx=55&ny=127&authKey=_sjLTPuER0qIy0z7hGdKSg")
# print(response.json())

if __name__ == '__main__':
    mcp.run(transport="streamable-http")
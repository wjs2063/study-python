import os
import sys
import urllib.request
import truststore
import json
import certifi
import ssl
from typing import Literal
import asyncio
from aiohttp import ClientSession, TCPConnector
from dotenv import load_dotenv

ssl_ctx = ssl.create_default_context(cafile=certifi.where())
truststore.inject_into_ssl()
load_dotenv()
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')


# encText = urllib.parse.quote("최신 뉴스")
# url = "https://openapi.naver.com/v1/search/news.json?query=" + encText  # JSON 결과
# # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
# request = urllib.request.Request(url)
# request.add_header("X-Naver-Client-Id", client_id)
# request.add_header("X-Naver-Client-Secret", client_secret)
# response = urllib.request.urlopen(request)
# rescode = response.getcode()
# if (rescode == 200):
#     response_body = response.read()
#     response = json.loads(response_body.decode('utf-8'))
#     for item in response['items']:
#         print("-" * 50)
#         print(item["title"])
#         print(item["description"])
# else:
#     print("Error Code:" + rescode)


async def get_naver_search(query: str, display: int, start: int, sort: Literal["sim", "date"] = "date") -> list[dict]:
    """
    네이버 API를 이용하여 사용자의 질문과 관련있는 뉴스를 list[dict]형식으로 반환합니다
    params query: 사용자의 질문으로부터 추출해낸 뉴스 검색 쿼리
    params display: 한번에 표시할 검색 결과 개수(기본 10,최대 100)
    params start: 검색 시작 위치(기본1, 최대 100)
    params sort: 검색 결과 정렬 방법(sim : 정확도순으로 내림차순 정렬, date : 날짜순으로 내림차순 정렬)
    """

    async with ClientSession(
            connector=TCPConnector(ssl=ssl_ctx),
            headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}) as session:
        async with session.get(url="https://openapi.naver.com/v1/search/news.json",
                               params={"query": query, "display": display, "start": start}) as response:
            response = await response.json()
            print(response)
            return response

    return []


async def main():
    print(await get_naver_search(query="최신 뉴스", display=10, start=1, sort="date"))


if __name__ == "__main__":
    asyncio.run(main())

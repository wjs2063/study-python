import asyncio

from mcp.server.fastmcp import FastMCP
import truststore
from aiohttp import ClientSession, TCPConnector
import json
from dotenv import load_dotenv
from enum import Enum
import truststore
import certifi
import ssl
from typing import Literal
import os
from dotenv import load_dotenv
ssl_ctx = ssl.create_default_context(cafile=certifi.where())

truststore.inject_into_ssl()


class SortType(str, Enum):
    """정렬 방식
    - sim : 정확도 순으로 내림차순 정렬
    - date: 날짜순으로 내림차순 정렬
    """
    sim = "sim"
    date = "date"


load_dotenv()

truststore.inject_into_ssl()
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

mcp = FastMCP(name="naver-search-mcp-server", host="0.0.0.0", port=8080)


@mcp.tool()
async def get_naver_search(query: str, display: int, start: int, sort: Literal["sim", "date"] = "date") -> dict:
    """
    Search Naver News and return the raw JSON response.

    Args:
        query: 사용자의 질문으로부터 추출해낸 뉴스 검색 쿼리
        display: 한번에 표시할 검색 결과 개수(기본 10,최대 100)
        start: 검색 시작 위치(기본1, 최대 100)
        sort: 검색 결과 정렬 방법(sim : 정확도순으로 내림차순 정렬, date : 날짜순으로 내림차순 정렬)

    Returns: dict: 네이버 뉴스 검색 API의 원본 JSON 응답(예: total: 총 검색 결과 개수, start : 검색 시작 위치, display : 한 번에 표시할 검색 결과 개수, items 등).

    """

    async with ClientSession(
            connector=TCPConnector(ssl=ssl_ctx),
            headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}) as session:
        async with session.get(url="https://openapi.naver.com/v1/search/news.json",
                               params={"query": query, "display": display, "start": start}) as response:
            response = await response.json()
            return response


# async def main():
#     print(await get_naver_search(query="최신 뉴스", display=10, start=1, sort="date"))


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

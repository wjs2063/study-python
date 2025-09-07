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
client_secret = os.getenv('NAVER_SECRET_KEY')

mcp = FastMCP(name="naver-search-mcp-server", host="0.0.0.0", port=8080)


@mcp.tool()
async def get_naver_news(query: str, display: int, start: int, sort: Literal["sim", "date"] = "date") -> dict:
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
            print(response)
            return response


@mcp.tool()
async def get_naver_poi_search(query: str, display: int, start: int, sort: Literal["random", "comment"]) -> dict:
    """
    Search Naver Local Search and return the raw JSON response.
    POI Data Like 맛집, 장소추천 등
    Args:
        query : 사용자의 질문으로부터 추출해낸 지역 검색 쿼리
        display: 한번에 표시할 검색 결과 개수(기본 1,최대 5)
        start: 검색 시작 위치(기본1, 최대 1)
        sort: 검색 결과 정렬 방법(random : 정확도순으로 내림차순 정렬, comment : 업체 및 기관에 대한 카페,블로그 리뷰 개수순 내림차순 정렬)

    Returns:
          dict

    """
    async with ClientSession(
            connector=TCPConnector(ssl=ssl_ctx),
            headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}) as session:
        async with session.get(url="https://openapi.naver.com/v1/search/local.json",
                               params={"query": query, "display": display, "start": start, "sort": sort}) as response:
            response = await response.json()
            return response


# async def main():
#     print(await get_naver_search(query="최신 뉴스", display=10, start=1, sort="date"))
from bs4 import BeautifulSoup
from readability import Document


async def fetch_news_text(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        async with session.get(url=url, headers=headers, timeout=15) as response:
            resp = await response.text()

    # readability로 핵심 본문 추출
    doc = Document(resp)
    summary_html = doc.summary(html_partial=True)

    # 본문 텍스트만 뽑기
    soup = BeautifulSoup(summary_html, "lxml")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"]) if p.get_text(strip=True)]
    text = "\n\n".join(paragraphs)
    return text.strip()


@mcp.tool()
async def get_news_data(url: str) -> str:
    """
    url link로 부터 뉴스 데이터를 읽어옵니다.
    Args:
        url: url링크

    Returns:
        뉴스 데이터
    """
    text = await fetch_news_text(url)
    return text


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

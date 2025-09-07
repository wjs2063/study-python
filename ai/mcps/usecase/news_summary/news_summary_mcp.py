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
from bs4 import BeautifulSoup
from readability import Document

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

            for result in response["items"]:
                text = await fetch_news_text(result["link"])
                result["text"] = text
            print(response)
            return response


import re
from urllib.parse import urlparse

from aiohttp import ClientSession, TCPConnector
from bs4 import BeautifulSoup, NavigableString
from readability import Document

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "Referer": "https://news.naver.com/",
}

# 네이버 본문 추출에 방해되는 요소들(추천 버튼/레이어, 공유, 구독, 광고 등)
NAVER_REMOVE_SELECTORS = [
    "#spiLayer", ".u_likeit", ".media_end_head_tool", ".media_end_head_more",
    ".subscribe_ct", ".media_end_categorize", ".media_end_head_font", ".media_end_kicker",
    ".media_end_head_info_datestamp", ".media_end_head_title", ".media_end_head_autosummary",
    ".end_btn", ".promotion", ".sns_share", ".newsct_related_article", ".newsct_related",
    ".ndlayer_open", ".media_end_linked_more", ".quick_menu", ".media_end_categorize_add",
    ".byline_sns", ".origin", ".copyright", ".reporter_area", ".channel_info",
]

def _clean_text(s: str) -> str:
    s = re.sub(r"\r\n?", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()

def _extract_text_from_container(container: BeautifulSoup) -> str:
    # 불필요한 태그 제거
    for sel in NAVER_REMOVE_SELECTORS:
        for tag in container.select(sel):
            tag.decompose()
    for tag in container.find_all(["script", "style", "noscript", "iframe", "button", "aside", "figure"]):
        tag.decompose()

    # 문단성 있는 것만 추출
    blocks = []
    for el in container.find_all(["p", "li", "h2", "h3", "blockquote"]):
        txt = el.get_text(" ", strip=True)
        if txt:
            blocks.append(txt)
    # 백업: 그래도 비면 전체 텍스트
    if not blocks:
        raw = container.get_text("\n", strip=True)
        return _clean_text(raw)
    return _clean_text("\n\n".join(blocks))

def _is_naver_news(netloc: str) -> bool:
    return any(netloc.endswith(d) for d in ["news.naver.com", "n.news.naver.com", "m.news.naver.com"])

async def _fetch_html(url: str) -> str:
    # ssl=False는 되도록 지양(보안/호환). 네이버는 정상 인증서이므로 True가 안전.
    async with ClientSession(headers=HEADERS, connector=TCPConnector(ssl=False)) as session:
        async with session.get(url, timeout=15, allow_redirects=True) as resp:
            resp.raise_for_status()
            # 인코딩 추론
            text = await resp.text()
            return text

async def fetch_news_text(url: str) -> str:
    html = await _fetch_html(url)
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    # 1) 네이버 특화 파서
    if _is_naver_news(netloc):
        soup = BeautifulSoup(html, "lxml")

        # 네이버(데스크탑/모바일)의 대표 본문 컨테이너 후보들
        # - 신형: #newsct_article, #dic_area
        # - 구형: #articleBodyContents, #articeBody(오타 케이스도 있어서 여분 포함)
        container = (
            soup.select_one("#newsct_article")
            or soup.select_one("#dic_area")
            or soup.select_one("#articleBodyContents")
            or soup.select_one("#articeBody")
            or soup.select_one(".newsct_article")
        )

        if container:
            text = _extract_text_from_container(container)
            if text:
                return text

        # 컨테이너를 못 찾았거나 비어 있으면 readability 폴백
        doc = Document(html)
        frag = doc.summary(html_partial=True)
        soup2 = BeautifulSoup(frag, "lxml")
        return _clean_text("\n\n".join(
            p.get_text(" ", strip=True)
            for p in soup2.find_all(["p", "li"])
            if p.get_text(strip=True)
        ))

    # 2) 그 외 도메인: readability 우선
    doc = Document(html)
    frag = doc.summary(html_partial=True)
    soup = BeautifulSoup(frag, "lxml")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"]) if p.get_text(strip=True)]
    if paragraphs:
        return _clean_text("\n\n".join(paragraphs))

    # 폴백: 전체 HTML에서 p만 긁기
    soup_full = BeautifulSoup(html, "lxml")
    ps = [p.get_text(" ", strip=True) for p in soup_full.find_all("p") if p.get_text(strip=True)]
    if ps:
        return _clean_text("\n\n".join(ps))

    # 최종 폴백: 전체 텍스트
    return _clean_text(soup_full.get_text("\n", strip=True))

@mcp.tool()
async def get_news_data(url: str) -> str:
    """
    url link로 부터 뉴스 본문을 읽어옵니다.
    Args:
        url: url링크

    Returns:
        뉴스 데이터
    """
    text = await fetch_news_text(url)
    print(text)
    return text


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

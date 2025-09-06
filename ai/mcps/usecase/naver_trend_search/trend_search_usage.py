import os

from aiohttp import ClientSession, TCPConnector
import traceback
import ssl
from mcp.server.fastmcp import FastMCP
import asyncio
from dotenv import load_dotenv
load_dotenv()
url = "https://openapi.naver.com/v1/datalab/search"


async def get_trend_search():
    """
    그룹으로 묶은 검색어에 대한 네이버 통합검색에서 검색 추이 데이터를 JSON 형식으로 반환합니다.
    Returns:

    """
    headers = {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_SECRET_KEY"),
    }
    data = {
        "startDate": "2025-09-01",
        "endDate": "2025-09-06",
        "timeUnit": "date",
        "keywordGroups": [
            {
                "groupName": "범죄",
                "keywords": [
                    "정치인",
                ]
            }
        ]
    }

    async with ClientSession(headers=headers, connector=TCPConnector(ssl=False)) as session:
        async with session.post(url=url, headers=headers, json=data) as response:
            response = await response.json()
            print(response)
            return response


if __name__ == '__main__':
    asyncio.run(get_trend_search())

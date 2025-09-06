import os

from aiohttp import ClientSession, TCPConnector
import traceback
import ssl

from docutils.nodes import description
from mcp.server.fastmcp import FastMCP
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

load_dotenv()
url = "https://openapi.naver.com/v1/datalab/search"

mcp = FastMCP(name="naver trend search", host="0.0.0.0", port=8080)


class KeywordGroup(BaseModel):
    groupName: str = Field(description="주제어. 검색어 묶음을 대표하는 이름입니다.")
    keywords: list[str] = Field(description="주제어에 해당하는 검색어. 최대 20개의 검색어를 배열로 설정할 수 있습니다.")


class TrendData(BaseModel):
    period: str = Field(description="구간별 시작 날짜(yyyy-mm-dd 형식)")
    ratio: float = Field(description="	구간별 검색량의 상대적 비율. 구간별 결과에서 가장 큰 값을 100으로 설정한 상댓값입니다.")


class TrendResult(BaseModel):
    title: str = Field(description="주제어")
    keywords: list = Field(description="주제어에 해당하는 검색어")
    data: list[TrendData] = Field(description="구간별 트렌드 추이")


class TrendSearchResponse(BaseModel):
    start_date: str = Field(description="조회 기간 시작 날짜(yyyy-mm-dd 형식).")
    end_date: str = Field(description="조회 기간 종료 날짜(yyyy-mm-dd 형식)")
    time_unit: str = Field(description="구간 단위")
    results: list[TrendResult] = Field(description="")
    class Config:
        alias_generator = to_camel
        populate_by_name = True

@mcp.tool()
async def get_trend_search(start_date: str, end_date: str, time_unit: str,
                           keywordGroups: list[KeywordGroup]) -> TrendSearchResponse:
    """
    그룹으로 묶은 검색어에 대한 네이버 통합검색에서 검색 추이 데이터를 JSON 형식으로 반환합니다.
    Args:
        start_date: yyyy-mm-dd
        end_date: yyyy-mm-dd
        time_unit: "date","week","month"
        keywordGroups: list[KeywordGroup]

    Returns:

    """

    headers = {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_SECRET_KEY"),
    }
    data = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": [
            keyword.model_dump()
            for keyword in keywordGroups
        ]
    }

    async with ClientSession(headers=headers, connector=TCPConnector(ssl=False)) as session:
        async with session.post(url=url, headers=headers, json=data) as response:
            response = await response.json()
            return TrendSearchResponse(**response)


if __name__ == '__main__':
    mcp.run(transport="streamable-http")

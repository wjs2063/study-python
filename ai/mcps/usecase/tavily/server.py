from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.server import FastMCP
from langchain_tavily import TavilySearch, TavilyExtract
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from typing import Optional, Literal, List, Union
import truststore
import certifi

print(certifi.where())

truststore.inject_into_ssl()
load_dotenv()

mcp = FastMCP(host="0.0.0.0", port=8000, name="tavily_mcp_server", streamable_http_path="/mcp", sse_path="/mcp",
              stateless_http=True)


@mcp.tool(name="tavily_search_tool", title="Tavily Search", description="tavily search assistant tool for user query")
async def search_web(query: str, name: str = "tavily_search", include_domains: Optional[list[str]] = None,
                     search_depth: Optional[Literal["basic", "advanced"]] = None,
                     include_images: Optional[bool] = None, exclude_domains: Optional[List[str]] = None,
                     max_results: Optional[int] = None, topic: Optional[Literal["general", "news", "finance"]] = None,
                     include_answer: Optional[Union[bool, Literal["basic", "advanced"]]] = None):
    """
    :param query: 검색할 키워드 또는 질문
    :param name: 도구 이름
    :param include_domains: 포함할 도메인 리스트
    :param search_depth: 검색 깊이 ("basic" : 빠른 검색, "advanced":상세 검색)
    :param include_images: 이미지 포함 여부 ex(False,True)
    :param exclude_domains: 제외할 도메인 리스트
    :param max_results: 검색결과 최대 길이
    :param topic: 검색 주제 필터
    :param include_answer: 쿼리에 맞는 간결한 대답여부,
    :return:
    """
    tavily_search = TavilySearch(name=name, include_domains=include_domains, search_depth=search_depth,
                                 include_images=include_images, exclude_domains=exclude_domains,
                                 max_results=max_results, topic=topic, include_answer=include_answer)
    return await tavily_search.ainvoke(query)


@mcp.tool(name="test_tool", title="test_tool_title", description="test tool title")
async def test_tool(query: str):
    return "너의 질문은 : " + query


if __name__ == "__main__":
    mcp.run(transport="sse")

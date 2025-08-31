from mcp.server.fastmcp import FastMCP

import http.client, urllib.parse
import truststore
from datetime import datetime,timedelta
import json
from dotenv import load_dotenv
import os
truststore.inject_into_ssl()
load_dotenv()
api_token = os.getenv("THE_NEWS_API_TOKEN")
mcp = FastMCP(name="get news", host="0.0.0.0", port=8080, mount_path="/mcp")


@mcp.tool()
async def get_news(search_keyword: str, categories: list[str],days_ago:int = -14) -> list[dict]:
    """

    :param search_keyword: 사용자의 질문과 관련된 뉴스검색쿼리
    :param days_ago: 현재시각으로부터 가져올 뉴스범위
    :param categories: 사용자의 질문과 관련된 카테고리 Supported categories: general | science | sports | business | health | entertainment | tech | politics | food | travel
    :return: list[dict]
    뉴스결과를 list 형태로 반환
    """
    conn = http.client.HTTPSConnection('api.thenewsapi.com')

    params = urllib.parse.urlencode({
        'api_token': api_token,
        'published_after' : (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S"),
        'categories': ", ".join(categories),
        'search': search_keyword,
        'limit': 2,
    })

    conn.request('GET', '/v1/news/all?{}'.format(params))

    res = conn.getresponse()
    datas = res.read()
    datas = json.loads(datas.decode('utf-8'))
    results = []
    results.extend(
        [{"title": data["title"], "description": data["description"], "published_at": data["published_at"]} for data in
         datas["data"]])
    return results


if __name__ == '__main__':
    mcp.run(transport="streamable-http")

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from aiohttp import ClientSession, TCPConnector
import os
import truststore
import certifi
import ssl

ssl_ctx = ssl.create_default_context(cafile=certifi.where())

truststore.inject_into_ssl()
load_dotenv()

mcp = FastMCP(name="weather_apihub_mcp", host="0.0.0.0", port=8080)
api_key = os.getenv("OPEN_APIHUB_KEY")

format_announce = lambda s: (
    f"{s[:4]}년 {s[4:6]}월 {s[6:8]}일 {s[8:10]}시 {s[10:12]}분"
    if isinstance(s, str) and len(s) >= 12 else "정보없음"
)
# 2) 라벨과 포맷터를 함께 보관: (label, formatter or None)
description_map = {
    "announceTime": ("발표시각", format_announce),
    "rnST": ("강수확률", None),
    "wfCd": ("날씨코드(하늘상태)", None),
    "wd1": ("풍향(1)", None),
    "wd2": ("풍향(2)", None),
    "ta": ("예상기온(℃)", None),
    "wf": ("날씨", None),
    "rnYn": ("강수형태", None),
}


@mcp.tool()
async def get_weather_information(page_no: int, num_of_rows: int, reg_id: str) -> str:
    """
    한국지역의 육상예보조회API입니다. 기온,강수확률,풍향,풍속,하늘상태,강수상태에 대한 기상정보를 가져올 수 있습니다
    page_no <= totalCount이면 계속 가져올수있습니다.

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
        str
        날씨정보를 문자열로 리턴합니다.


    """
    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": "JSON",
        "regId": reg_id,
        "authKey": api_key

    }
    async with ClientSession(connector=TCPConnector(ssl=ssl_ctx)) as session:
        async with session.get(url="https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstMsgService/getLandFcst",
                               params=params) as response:
            response = await response.json()
            print(response)
            return get_description(response["response"]["body"]["items"]["item"][0])


def get_description(data: dict) -> str:
    lines = ["날씨정보는 아래와 같습니다."]
    for key, (label, formatter) in description_map.items():
        raw = data.get(key)
        raw_str = str(raw) if raw is not None else None
        if formatter:
            value = formatter(raw_str)
        else:
            value = raw_str if raw_str is not None else "정보없음"
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)


if __name__ == '__main__':
    mcp.run(transport="streamable-http")

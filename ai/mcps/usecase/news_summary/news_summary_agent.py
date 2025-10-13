from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import asyncio
from datetime import datetime


now = datetime.now()
current_date_string = now.strftime("%Y-%m-%d")
print(current_date_string)

async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "naver_news_server": {"url": "http://localhost:8080/mcp", "type": "streamble-http"},
            "mail_sender_server" : {"url":"http://localhost:8082/mcp","type": "streamble-http"},
        }
    }

    client = MCPClient.from_dict(config=config)

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = MCPAgent(llm=llm, client=client, max_steps=20,
                     system_prompt=f"""
                     너는 뉴스 데이터 수집 Agent 야, 
                     뉴스 url로부터 뉴스 본문을 읽어올수있고 메일을 전달할수있어
                     *반드시 주어진링크의 본문을 읽어서 최소 4줄이상이되도록 요약을 포함하고, link를 포함하도록해*
                     *제목형식은 yyyy-mm-dd [제목] 형식으로 보내*
                     
                     현재시각은 {current_date_string}
                     주어진 도구를 적절하게 사용하여 사용자에게 뉴스 요약 메일을 보내줘!
                     """,
                     use_server_manager=True,
                     )

    results = await agent.run("K 패션 관련  뉴스 . dbwlsdl2719@naver.com으로 보내줘")
    print(results)



if __name__ == '__main__':
    asyncio.run(main())

from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import asyncio


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

    agent = MCPAgent(llm=llm, client=client, max_steps=10,
                     system_prompt="""
                     너는 뉴스 데이터 수집 Agent 야, 
                     뉴스 url로부터 뉴스 본문을 읽어올수있고 메일을 전달할수있어
                     *반드시 주어진링크의 본문을 읽어서 최소 4줄이상이되도록 요약을 포함하고, link를 포함하도록해*
                     주어진 도구를 적절하게 사용하여 사용자에게 뉴스 요약 메일을 보내줘!
                     """,
                     use_server_manager=True,
                     )

    results = await agent.run("현대오토에버 관련 뉴스. jahy5352@naver.com으로 보내줘")



if __name__ == '__main__':
    asyncio.run(main())

from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import asyncio


async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "naver_news_server": {"url": "http://localhost:8080/mcp", "type": "streamble-http"}
        }
    }

    client = MCPClient.from_dict(config=config)

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = MCPAgent(llm=llm, client=client, max_steps=5,
                     system_prompt="너는 트렌트 추이 분석 Agent야 사용자의 질문에 대한 검색추이데이터를 분석해 ")

    results = await agent.run("대통령 검색 추이")

    print(results)


if __name__ == '__main__':
    asyncio.run(main())

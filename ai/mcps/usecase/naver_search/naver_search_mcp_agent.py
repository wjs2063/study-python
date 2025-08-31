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
                     system_prompt="너는 뉴스 요약 및 맛집추천 Agent야, 해당 도구를 적절하게 사용하여 사용자에게 적절한 응답을 요약해줘")

    results = await agent.run("삼성역 코엑스 맛집추천")

    print(results)


if __name__ == '__main__':
    asyncio.run(main())

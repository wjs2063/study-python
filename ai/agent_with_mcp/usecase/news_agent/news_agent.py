from mcp_use import MCPAgent,MCPClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import asyncio


async def main():

    load_dotenv()

    config = {
        "mcpServers": {
            "news_mcp_server": {"url":"http://localhost:8080/mcp","type":"streamble-http"}
        }
    }

    client = MCPClient.from_dict(config=config)


    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = MCPAgent(llm=llm,client=client,max_steps=5,system_prompt="너는 뉴스 요약 Agent야, 뉴스요약과 함께 뉴스 발행일자를 꼭 명시해서 사용자에게 알려줘")

    results = await agent.run("비트코인 살까 말까")

    print(results)

if __name__ == '__main__':
    asyncio.run(main())
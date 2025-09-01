from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from datetime import datetime
import os
import asyncio


async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "weather_mcp_server": {"url": "http://localhost:8080/mcp", "type": "streamble-http"}
        }
    }

    client = MCPClient.from_dict(config=config)

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = MCPAgent(llm=llm, client=client, max_steps=5,
                     system_prompt=f"날씨 기상캐스터 Agent야 해당 툴을 적절하게사용하여 날씨정보를 전달해줘, 현재 시각은 {datetime.now().strftime("%Y%m%d")}")

    results = await agent.run("서울 날씨")

    print(results)


if __name__ == '__main__':
    asyncio.run(main())

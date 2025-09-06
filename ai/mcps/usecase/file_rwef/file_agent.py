from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import asyncio


async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "file_rwfs_server": {"url": "http://localhost:8080/mcp", "type": "streamble-http"}
        }
    }

    client = MCPClient.from_dict(config=config)

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = MCPAgent(llm=llm, client=client, max_steps=5,
                     system_prompt="서버내에있는 파일명과 파일내용을 요약해주는 요약전문가 Agent야")

    results = await agent.run("서버에있는 내용 요약해봐")

    print(results)


if __name__ == '__main__':
    asyncio.run(main())

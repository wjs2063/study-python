import asyncio

from fastmcp.client import Client
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import truststore

truststore.inject_into_ssl()
load_dotenv()

#chat_openai = ChatOpenAI()

client = Client("http://localhost:8000/mcp")


async def main():

    async with client:
        print(client.is_connected())
        tools = await client.list_tools()
        print(tools)


        #tool_response = await client.call_tool(name="tavily_search_tool",arguments={"query":"공각기동대"})
        tool_response = await client.call_tool(name="test_tool",arguments={"query":"테스트 질문"})
        print(tool_response)




asyncio.run(main())
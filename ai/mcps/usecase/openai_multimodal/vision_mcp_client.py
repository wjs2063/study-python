import asyncio

from fastmcp.client import Client
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import truststore
import base64

truststore.inject_into_ssl()
load_dotenv()

# chat_openai = ChatOpenAI()

client = Client("http://localhost:9090/mcp")


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your imageå
image_path = "sinjjang.jpeg"

# Getting the Base64 string
base64_image = encode_image(image_path)


async def main():
    async with client:
        tools = await client.list_tools()
        # tool_response = await client.call_tool(name="tavily_search_tool",arguments={"query":"공각기동대"})
        tool_response = await client.call_tool(name="explanation_image",
                                               arguments={"query": "이미지에 대한 설명", "base64_image":base64_image})

        print(tool_response)

asyncio.run(main())

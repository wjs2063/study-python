from sys import base_exec_prefix

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from openai.types.responses import ResponseInputTextParam, ResponseInputImageParam, ResponseInputFileParam,Response
from openai.types.responses.response_input_param import Message
load_dotenv()
from openai import OpenAI,AsyncOpenAI

client = AsyncOpenAI()

mcp = FastMCP(name="visionapi_mcp_server",host="0.0.0.0",port=9090)



@mcp.tool(name="explanation_image")
async def explanation_image(base64_image:str) -> Response :
    base_64_img = f"data:image/jpeg;base64,{base64_image}"
    response = await client.responses.create(
        model="gpt-4.1",
        input=[
            Message(
                role="user", content=[
                    ResponseInputTextParam(type="input_text", text="이 이미지를 보고 한국어로 설명해줘"),
                    ResponseInputImageParam(type="input_image", image_url=base_64_img)

                ]
            )
        ],
    )
    print(response)
    return response


if __name__ == "__main__":

    mcp.run(transport="streamable-http")
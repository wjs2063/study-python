import base64
from openai import OpenAI
from openai.types.responses import ResponseInputTextParam, ResponseInputImageParam, ResponseInputFileParam,Response
from openai.types.responses.response_input_param import Message
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "tattoosinjjang.jpeg"

# Getting the Base64 string
base64_image = encode_image(image_path)

response = client.responses.create(
    model="gpt-4.1",
    input=[
        Message(
            role="user", content=[
                ResponseInputTextParam(type="input_text", text="이 이미지를 보고 한국어로 설명해줘"),
                # { "type": "input_text", "text": "이 이미지를 보고 한국어로 설명해줘" },
                ResponseInputImageParam(type="input_image", image_url=f"data:image/jpeg;base64,{base64_image}")
                # {
                #     "type": "input_image",
                #     "image_url": f"data:image/jpeg;base64,{base64_image}",
                # }

            ]
        )
    ],
)

print(response.output_text)

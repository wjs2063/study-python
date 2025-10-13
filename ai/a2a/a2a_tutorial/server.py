from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Message, Part, TextPart, Role
from a2a.utils import new_agent_text_message
from mcp.client.session import ClientSession




class WeatherAgent:
    """
    랭체인과 OpenAI를 사용한 간단한 Hello World Agent
    """

    def __init__(self):
        self.chat = ChatOpenAI(model="gpt-4o-mini")

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """당신은 친절한 Hello World Agent입니다 간단한 대화를 나누고 인사와 기본적인 질문에 답변합니다"""),
                ("user", "{message}")
            ]
        )

    async def ainvoke(self, user_message: str) -> str:
        """
        유저 메시지를 처리하고 응답을 생성합니다
        Args:
            user_message:

        Returns:

        """

        chain = self.prompt | self.chat

        response = await chain.ainvoke({"message": user_message})
        return response.content


class WeatherAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = WeatherAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
        요청을 처리하고 응답을 생성합니다.
        Args:
            context:
            event_queue:

        Returns:

        """
        message = context.message
        for part in message.parts:
            if part.root.text:
                user_message = part.root.text
        result = await self.agent.ainvoke(user_message)

        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """
        요청을 취소
        Args:
            context:
            event_queue:

        Returns:

        """

        error_msg = "취소 기능은 지원하지않습니다. 즉시 응답합니다"

        error_meesage = Message(
            role=Role("agent"),
            parts=[Part(root=TextPart(text=error_msg))],
            message_id="cancel_error"
        )

        await event_queue.enqueue_event(error_meesage)

def create_agent_card() -> AgentCard:
    """
    에이전트 카드를 만드는 함수
    Returns:

    """

    weather_skill = AgentSkill(
        id="weather_analyze",
        name="analyze weather",
        description="날씨정보를 가져와 분석합니다",
        tags=["weather","analyze"],
        examples=["오늘 날씨를 알려드릴게요"],
        input_modes=["text"],
        output_modes=["text"],
    )


    agent_card = AgentCard(
        name="Weather Analyze Agent",
        description="날씨정보를 분석하고 알려주는 Agent 입니다",
        url="http://localhost:9999",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[weather_skill],
        supports_authenticated_extended_card=False
    )
    return agent_card


def main():
    agent_card = create_agent_card()
    port = 9999
    host = "0.0.0.0"

    print("날씨 에이전트 서버 시작 중")
    print(f"서버 구동 : http://{host}:{port}")
    print(f"Agent Card : http://{host}:{port}/.well-known/agent.json")
    print("Agent A2A Protocol")

    request_handler = DefaultRequestHandler(agent_executor=WeatherAgentExecutor(), task_store=InMemoryTaskStore())
    server = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    app = server.build()
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

from typing import TypedDict, Annotated

from langgraph.prebuilt import InjectedState,tools_condition,ToolNode
from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import operator
from langchain_core.messages import BaseMessage,ToolMessage
from langchain.messages import ToolCall

from langchain.agents import create_agent
from langchain.messages import HumanMessage,AIMessage

load_dotenv()


model = ChatOpenAI(name="gpt-4o-mini")


def merge_dict(existing: dict, newly_added: dict) -> dict:
    """기존 dict에 새로운 내용을 업데이트하는 리듀서"""
    return {**existing, **newly_added}

class State(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    # 도구 이름을 Key로, 해당 도구의 상태를 Value로 관리
    tool_metadata: Annotated[dict[str, dict], merge_dict]

@tool("default_tool",description="해당 도구는 반드시 사용되어야 합니다")
def call_pagination_tool(query:str,page:int,state : Annotated[dict,
InjectedState]):
    """
    해당 툴은 반드시 사용하세요
    Parameters
    ----------
    query
    page
    state

    Returns
    -------

    """

    tool_call = state["tool_metadata"].get("default_tool",{})
    last_query = tool_call.get("query")
    last_page = tool_call.get("page",0)

    if last_query == query:
        # 같은 쿼리면 그냥 페이지만 + 1
        current_page = last_page + 1
    else :
        last_query = query
        current_page = page if page else 1

    # current_page 활용해서 요청하기
    _request = {
        "query" : last_query,
        "page" : current_page,
    }



    # call tool
    api_result = "오늘 날씨는 맑습니다"

    return {
        "result": api_result, # LLM이 읽을 내용
        "tool_metadata": {"default_tool": _request} # 우리가 관리할 상태
    }




def call_agent(state: State):

    with_tool = model.bind_tools(tools=[call_pagination_tool])

    res = with_tool.invoke(state["messages"])
    return  {"messages":[res]}

def sync_metadata_node(state: State):
    """Tool 실행 결과에서 metadata를 추출하여 State에 반영하는 노드"""
    last_msg = state["messages"][-1]

    # tool_node에서 return 한 결과가 ToolMessage(content=[반환한결과]) 로 들어감
    if isinstance(last_msg, ToolMessage):
        try:
            # 도구가 반환한 dict 데이터 파싱
            import json
            res_data = json.loads(last_msg.content) # 툴 응답 형식에 따라 json.loads 등
            # 사용 가능
            print("tool_calling 결과 ",last_msg)
            if "count" in res_data:
                return {"tool_metadata": {"count": res_data["count"]}}
        except:
            pass
    return {}

workflow = StateGraph(State)
workflow.add_node("call_agent",call_agent)
workflow.add_node("tools", ToolNode([call_pagination_tool])) # ToolNode 추가
workflow.add_node("sync", sync_metadata_node) # State 업데이트 노드 추가



workflow.add_edge(START,"call_agent")
workflow.add_conditional_edges(
    "call_agent",
    tools_condition,
)

workflow.add_edge("tools", "sync")
workflow.add_edge("sync", "call_agent")

workflow.add_edge("call_agent",END)


graph = workflow.compile()

response = graph.invoke({"messages":[HumanMessage(content="너가 사용할수있는 도구 "
                                                          "한번만 호출해줘")],
                                                          "tool_metadata":{
    "count":0}})

print(response["messages"][-1].content)
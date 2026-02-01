from typing import TypedDict, Annotated

from langgraph.prebuilt import InjectedState,tools_condition,ToolNode
from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import operator
from langchain_core.messages import BaseMessage,ToolMessage

from langchain.agents import create_agent
from langchain.messages import HumanMessage,AIMessage

load_dotenv()


model = ChatOpenAI(name="gpt-4o-mini")


class State(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    tool_metadata: dict

@tool("default_tool",description="해당 도구는 반드시 사용되어야 합니다")
def call_pagination_tool(query:str,state : Annotated[dict,InjectedState]):
    """
    해당 툴을 반드시 사용하여 응답하세요
    Parameters
    ----------
    query
    state

    Returns
    -------

    """
    metadata = state["tool_metadata"]
    print("tool 콜링되었음",metadata)

    # call tool

    return {"count" : metadata["count"] + 1}




def call_agent(state: State):

    with_tool = model.bind_tools(tools=[call_pagination_tool])

    res = with_tool.invoke(state["messages"])
    print("call_agent",state)
    return  {"messages":[res]}

def sync_metadata_node(state: State):
    """Tool 실행 결과에서 metadata를 추출하여 State에 반영하는 노드"""
    last_msg = state["messages"][-1]
    print("sync_metadata_node : state -> ",state)
    print("sync_metadata_node 결과 : ",last_msg,type(last_msg))

    if isinstance(last_msg, ToolMessage):
        try:
            # 도구가 반환한 dict 데이터 파싱
            import json
            res_data = eval(last_msg.content) # 툴 응답 형식에 따라 json.loads 등 사용 가능
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

print(response)
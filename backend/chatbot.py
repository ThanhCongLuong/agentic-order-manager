from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    order_id: str
    order_status: str

memory = MemorySaver()

def create_chatbot_graph(assistant_node_func):
    workflow = StateGraph(State)
    workflow.add_node("assistant", assistant_node_func)
    workflow.set_entry_point("assistant")
    workflow.add_edge("assistant", END)
    return workflow.compile(checkpointer=memory)
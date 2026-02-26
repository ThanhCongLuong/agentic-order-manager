from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from chatbot import create_chatbot_graph
from nodes import assistant_node
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from database import (init_db, 
    get_pending_requests, 
    approve_request, 
    refuse_request, 
    get_all_products, 
    update_status, 
    get_new_notifications)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])    

class ChatRequest(BaseModel):
    message: str

graph = create_chatbot_graph(assistant_node)

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    config = {"configurable": {"thread_id": "1"}} 
    
    inputs = {"messages": [HumanMessage(content=req.message)]}
    
    result = await graph.ainvoke(inputs, config=config) 
    
    return {"response": result["messages"][-1].content}

@app.get("/admin/requests")
async def list_requests():
    return get_pending_requests()

@app.post("/admin/approve/{req_id}")
async def approve(req_id: int):
    approve_request(req_id)
    return {"status": "success"}

@app.post("/admin/refuse/{req_id}")
async def refuse(req_id: int):
    refuse_request(req_id)
    return {"status": "success"}

@app.get("/products")
async def api_get_products():
    data = get_all_products()
    return {"products": data}

@app.post("/admin/update/{req_id}")
async def update_api(req_id: int):
    update_status(req_id)
    return {"status": "success"}

@app.get("/notifications")
async def check_notifications():
    new_actions = get_new_notifications()
    return {"notifications": new_actions}
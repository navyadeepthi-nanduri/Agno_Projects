from fastapi import FastAPI
from pydantic import BaseModel
from router import handle_query

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    result = handle_query(req.message)
    return {"response": result}
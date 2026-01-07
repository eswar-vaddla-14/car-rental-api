from fastapi import APIRouter
from pydantic import BaseModel
from app.chat import CHAT_CONTEXT, CHAT_STATE

human_router = APIRouter()

class HumanMessage(BaseModel):
    chat_id: str
    agent_id: str
    message: str

@human_router.post("/message")
async def human_message(req: HumanMessage):

    if CHAT_STATE.get(req.chat_id) != "HUMAN":
        return {
            "error": "This chat is not assigned to human support."
        }

    CHAT_CONTEXT[req.chat_id].append({
        "role": "agent",
        "content": req.message
    })

    return {
        "chat_id": req.chat_id,
        "reply": "Message sent to user",
        "mode": "HUMAN",
        "detail": CHAT_CONTEXT[req.chat_id]
    }
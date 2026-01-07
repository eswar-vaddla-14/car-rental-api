from fastapi import APIRouter
from pydantic import BaseModel
from app.chat import CHAT_CONTEXT, CHAT_STATE

user_router = APIRouter()

class UserMessage(BaseModel):
    user_id: str
    chat_id: str
    message: str

@user_router.post("/message")
async def user_message(req: UserMessage):

    if CHAT_STATE.get(req.chat_id) != "HUMAN":
        return {
            "error": "This chat is not assigned for human support."
        }
    
    CHAT_CONTEXT[req.chat_id].append({
        "role": "user",
        "content": req.message
    })

    return {
        "chat_id": req.chat_id,
        "reply": "Message sent to agent",
        "mode": "HUMAN",
        "detail": CHAT_CONTEXT[req.chat_id]
    }
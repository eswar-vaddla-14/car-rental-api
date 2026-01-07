from fastapi import Depends, FastAPI
from app.auth import verify_api_key
from app.chat import chat_router
from app.human import human_router
from app.user import user_router

app = FastAPI(title="Rent n Rides API")

app.include_router(
    router = chat_router,
    prefix = "/chat",
    dependencies = [Depends(verify_api_key)],
)

app.include_router(
    router = human_router,
    prefix = "/human",
    dependencies = [Depends(verify_api_key)]
)

app.include_router(
    router = user_router,
    prefix = "/user",
    dependencies = [Depends(verify_api_key)],
)

@app.get("/testroute", dependencies=[Depends(verify_api_key)])
async def route_test():
    response = {
        "status": "route is working properly",
    }
    return response

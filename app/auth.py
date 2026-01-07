from fastapi import Header, HTTPException
from app.config import CAR_RENTAL_API_KEY

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != CAR_RENTAL_API_KEY:
        raise HTTPException(
            status_code = 401,
            detail = "API Key is Missing or Invalid",
        )
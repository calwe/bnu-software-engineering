from fastapi import FastAPI
from pydantic import BaseModel
import logging
import uuid
from uuid import UUID
from typing import Dict
import time
import jwt
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", 24 * 60 * 60))
JWT_SECRET = os.getenv("JWT_SECRET", "secret") 

class Login(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    expires_in: int

class Session(BaseModel):
    session_id: str
    sub: str
    iat: int
    exp: int

session_data = {}

@app.post("/login/")
def login(login: Login) -> LoginResponse:
    session_id = str(uuid.uuid4())
    created_at = int(time.time())
    expires_at = created_at + JWT_EXPIRY
    session = {
        "session_id": session_id,
        "sub": login.username,
        "iat": created_at,
        "exp": expires_at
    }

    logger.info(f"Created session: {session}")
    
    encoded_jwt = jwt.encode(session, JWT_SECRET, algorithm="HS256")
    session_data[session_id] = session

    return { 
        "token": encoded_jwt,
        "expires_in": JWT_EXPIRY
    }


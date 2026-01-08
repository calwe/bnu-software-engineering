from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uuid
# from uuid import UUID
import time
import jwt
import os
from typing import Dict, Any
from app.auth import verify_user

# ===============================
# Logging configuration
# ===============================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================
# App initialisation
# ===============================

app = FastAPI()

# ===============================
# CORS configuration
# ===============================

cors_origins = os.getenv("CORS_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# JWT configuration
# ===============================

JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", 24 * 60 * 60))
JWT_SECRET = os.getenv("JWT_SECRET", "secret") 
JWT_ALGORITHM = "HS256"

# ===============================
# Pydantic models
# ===============================

class Login(BaseModel):
    """
    Represents user login credentials.
    """
    username: str
    password: str

class LoginResponse(BaseModel):
    """
    Reponse returned after successful authentication.
    """
    token: str
    expires_in: int

class Session(BaseModel):
    """
    JWT session payload structure.
    """
    session_id: str
    sub: str
    iat: int
    exp: int

# ===============================
# API endpoints
# ===============================

@app.post("/login", response_model=LoginResponse)
def login(login: Login):
    """
    Authenticates a user and returns a signed JWT.
    Password validation is omitted for demonstration purposes.
    """
    try:
        session_id = str(uuid.uuid4())
        created_at = int(time.time())
        expires_at = created_at + JWT_EXPIRY

        session: Dict[str, Any] = {
            "session_id": session_id,
            "sub": login.username,
            "iat": created_at,
            "exp": expires_at
        }
        
        encoded_jwt = jwt.encode(session, JWT_SECRET, algorithm=JWT_ALGORITHM)

        logger.info(f"Session created for user: {login.username}")

        return LoginResponse(
            token=encoded_jwt,
            expires_in=JWT_EXPIRY
        )
    except Exception as e:
        logger.exception("Failed to create JWT")
        raise HTTPException(status_code=500, detail="Failed to create authentication token")

@app.get("/getSession")
def get_session(user=Depends(verify_user)):
    """
    Returns the decoded JWT payload for the authenticated user.
    """
    return user

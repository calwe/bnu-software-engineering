from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import jwt
import os

logger = logging.getLogger(__name__)

security = HTTPBearer()

# For demonstration purposes only. In production, use a secure method to manage secrets.
JWT_SECRET = os.getenv("JWT_SECRET", "secret") 
JWT_ALGORITHM = "HS256"

async def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the JWT token provided in the Authorization header.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Log minimal non-sensitive info  
        user_identifier = payload.get("sub", "unknown_user")
        logger.info(f"Authenticated user: {user_identifier}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.error("Authentication failed: Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.InvalidTokenError:
        logger.error(f"Invalid token: {token}")
        raise HTTPException(status_code=401, detail="Invalid token")
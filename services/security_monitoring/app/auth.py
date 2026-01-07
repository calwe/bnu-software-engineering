from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import jwt
import os

logger = logging.getLogger(__name__)

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "secret") 

async def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  try:
      payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
      logger.info(f"Authenticated user: {payload}")
      return payload
  except jwt.InvalidTokenError:
      logger.error(f"Invalid token: {token}")
      raise HTTPException(status_code=401, detail="Invalid token")

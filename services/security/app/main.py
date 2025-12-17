from fastapi import FastAPI
from app.security import router as security_router

app = FastAPI()

app.include_router(security_router, prefix="/security")
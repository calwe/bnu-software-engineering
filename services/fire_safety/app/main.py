from fastapi import FastAPI
from app.fire_safety import router as fire_safety_router

app = FastAPI()

app.include_router(fire_safety_router, prefix="/fire_safety")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.fire_safety import router as fire_safety_router
import os

app = FastAPI()

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fire_safety_router, prefix="/fire_safety")
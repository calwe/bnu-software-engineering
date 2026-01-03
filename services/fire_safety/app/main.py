from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.fire_safety import router as fire_safety_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fire_safety_router, prefix="/fire_safety")
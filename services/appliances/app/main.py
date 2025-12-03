from fastapi import FastAPI
from app.appliances import router as appliances_router

app = FastAPI()

app.include_router(appliances_router, prefix="/appliances")
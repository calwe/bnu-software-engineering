from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.appliances import router as appliances_router
import os
import logging

# ===============================
# Logging configuration
# ===============================

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

logger.info(f"CORS configured for origins: {cors_origins}")

# ===============================
# Routers
# ===============================

app.include_router(appliances_router, prefix="/appliances")
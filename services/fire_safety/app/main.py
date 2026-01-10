from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.fire_safety import router as fire_safety_router
import os
import logging

# ===============================
# Logging configuration
# ===============================

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

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

app.include_router(fire_safety_router, prefix="/fire_safety")
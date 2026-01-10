from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user
import httpx
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ===============================
# Configuration
# ===============================

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

# ===============================
# Helper functions
# ===============================

async def change_door_lock(device_id: str, locked: bool, token: str):
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # update locked state door
            response = await client.post(
                f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/updateState",
                json={"state": "locked", "value": locked},
                headers={"Authorization": token},
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to change door state: {response.status_code}")
    except Exception as e:
        logger.error(f"Error updating door state: {e}")

# ===============================
# API endpoints
# ===============================

@router.get("/doors")
async def get_doors(request: Request, user = Depends(verify_user)):
    """
    Gets all door devices from appliances service.
    """

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""

    try:
        doors = {}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )

            response.raise_for_status()
            devices = response.json()
            
            # filter for just doors
            for device_id, device in devices.items():
                if device["type"] == "door":
                    doors[device_id] = device
        return doors
    except Exception as e:
        logger.error(f"Error getting doors: {e}")
        return {}

@router.post("/{device_id}/unlock")
async def unlock_door(device_id: str, request: Request, user = Depends(verify_user)):
    """
    Unlock a given door.
    """
    token = request.headers.get("Authorization")
    await change_door_lock(device_id, False, token)

@router.post("/{device_id}/lock")
async def lock_door(device_id: str, request: Request, user = Depends(verify_user)):
    """
    Lock a given door.
    """
    token = request.headers.get("Authorization")
    await change_door_lock(device_id, True, token)


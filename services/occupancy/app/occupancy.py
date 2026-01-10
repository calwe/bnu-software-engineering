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
# Pydantic model
# ===============================

class OccupancyResponse(BaseModel):
    message: str

# ===============================
# Configuration
# ===============================

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

# ==============================
# State
# ==============================

RoomsOccupancy : Dict[str, bool] = {}

# ===============================
# Helper functions
# ===============================

async def get_monitoring_devices(token: str):
    """
    Gets all camera and motion sensor devices from appliances service.
    """
    device_states: Dict[str, Dict] = {}

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )

            response.raise_for_status()
            devices = response.json()
            
            for device_id, device in devices.items():
                if device.get("type") in ("motion_sensor", "camera"):
                    room = device.get("room")
                    if not room:
                        logger.warning(f"Device {device_id} has no room assigned")
                        continue

                    device_states[device_id] = device
                    RoomsOccupancy.setdefault(room, False)

    except httpx.RequestError as e:
        logger.error(f"Appliances service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch devices: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error getting monitoring devices: {e}")

    return device_states

# ===============================
# API endpoints
# ===============================

@router.post("/occupancy_check", response_model=OccupancyResponse)
async def check_occupancy(request: Request, user = Depends(verify_user)):
    """
    Updates occupancy status of rooms based on monitoring devices.
    """
    # Extract token from request headers
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    try:
        # Get monitoring devices
        monitoring_device_states = await get_monitoring_devices(token)
        for device in monitoring_device_states.values():
            room = device.get("room")
            if room and device.get("states", {}).get("peopleDetected", False):
                RoomsOccupancy[room] = True
    
    except Exception as e:
        logger.error(f"Error in check_occupancy: {e}")
        
    return OccupancyResponse(message="Readings updated",)

@router.get("/", response_model=Dict[str, bool])
def get_occupancy(user = Depends(verify_user)):
    """
    Returns occupancy status of all rooms.
    """
    return RoomsOccupancy

@router.get("/{room}", response_model=Dict[str, bool])
def get_room_occupancy(room: str, user = Depends(verify_user)):
    """
    Returns occupancy status of a specific room.
    """
    if room not in RoomsOccupancy:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"occupied": RoomsOccupancy[room]}


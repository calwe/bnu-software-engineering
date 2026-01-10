from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Union, Dict, List
from app.auth import verify_user
import httpx
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ===============================
# Pydantic models
# ===============================

class SensorReadings(BaseModel):
    """
    Represents current environmental sensor readings.
    """
    temperature: float
    smoke_level: float

class SensorResponse(BaseModel):
    """
    Response returned after updating sensor readings.
    """
    message: str
    temperature: float
    smoke_level: float
    fire_active: bool

# ===============================
# Configuration
# ===============================

TEMPERATURE_THRESHOLD = 75.0 
SMOKE_THRESHOLD = 0.3  

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")
OCCUPANCY_SERVICE_URL = "http://occupancy:8000"

# ===============================
# State
# ===============================

current_readings: Dict[str, float] = {
    "temperature": 20.0,
    "smoke_level": 0.0
}

# Track previous threshold state
previous_threshold_state: bool = False

# ===============================
# Helper functions
# ===============================

async def get_occupancy_data(token: str):
    """
    Gets occupancy data from occupancy service.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{OCCUPANCY_SERVICE_URL}/occupancy/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch occupancy: {response.status_code}")
                return {}
            
            return response.json()
    except Exception as e:
        logger.error(f"Error getting occupancy data: {e}")
        return {}

async def get_fire_safety_devices(token: str) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
    """
    Gets all fire safety devices.
    """

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch devices: {response.status_code}")
                return {"alarms": [], "sprinklers": {}, "doors": []}
            
            devices = response.json()
            fire_devices = {
                "alarms": [],
                "sprinklers": {},
                "doors": []
            }
            
            for device_id, device in devices.items():
                device_type = device.get("type")
                device_name = device.get("name", "")
                
                if device_type == "fire_alarm":
                    fire_devices["alarms"].append(device_id)
                elif device_type == "sprinkler" or "sprinkler" in device_name.lower():
                    room = device.get("room", "unknown")
                    if room not in fire_devices["sprinklers"]:
                        fire_devices["sprinklers"][room] = []
                    fire_devices["sprinklers"][room].append(device_id)
                    logger.info(f"Added sprinkler {device_id} to room {room}")
                elif device_type == "door":
                    fire_devices["doors"].append(device_id)
            
            logger.info(f"Fire safety devices discovered: {fire_devices}")
            return fire_devices
    except Exception as e:
        logger.error(f"Error getting fire safety devices: {e}")
        return {"alarms": [], "sprinklers": {}, "doors": []}

async def toggle_devices(device_ids: list, state_name: str, value: Union[str, bool], token: str):
    """
    Toggles device states.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for device_id in device_ids:
                response = await client.post(
                    f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/updateState",
                    json={"state": state_name, "value": value},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to toggle device {device_id}: {e}")

# ===============================
# API endpoints
# ===============================

@router.get("/readings", response_model=SensorReadings)
def get_readings(user = Depends(verify_user)):
    """
    Get current sensor readings.
    """
    return current_readings

@router.post("/readings", response_model=SensorResponse)
async def update_readings(readings: SensorReadings, request: Request, user = Depends(verify_user)):
    """
    Updates sensor readings and trigger alarms if thresholds exceeded.
    """
    global previous_threshold_state
    
    logger.info(
        f"Sensor update received:"
        f"temperature={readings.temperature}, "
        f"smoke_level={readings.smoke_level}"
    )
    
    current_readings["temperature"] = readings.temperature
    current_readings["smoke_level"] = readings.smoke_level
    
    # Check current threshold state
    threshold_state = readings.temperature > TEMPERATURE_THRESHOLD or readings.smoke_level > SMOKE_THRESHOLD

    # Extract token from request headers
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    try:
        # Get fire safety devices
        fire_devices = await get_fire_safety_devices(token)
        
        if threshold_state:
            if not previous_threshold_state:
                logger.info("Thresholds exceeded - Activating alarms and unlocking doors...")
                
                if fire_devices["alarms"]:
                    logger.info(f"Activating {len(fire_devices['alarms'])} fire alarms")
                    await toggle_devices(fire_devices["alarms"], "status", "on", token)
                
                if fire_devices["doors"]:
                    logger.info(f"Unlocking {len(fire_devices['doors'])} doors")
                    await toggle_devices(fire_devices["doors"], "locked", False, token)
            
            # Check occupancy and control sprinklers per room
            if fire_devices["sprinklers"]:
                occupancy_data = await get_occupancy_data(token)
                
                for room_id, sprinkler_ids in fire_devices["sprinklers"].items():
                    is_occupied = occupancy_data.get(room_id, False)
                    
                    if not is_occupied:
                        logger.info(f"{room_id} is empty. Activating sprinklers...")
                        await toggle_devices(sprinkler_ids, "status", "on", token)
                    else:
                        logger.info(f"{room_id} is occupied. Keeping sprinklers off...")
                        
        else:
            if previous_threshold_state:
                logger.info("Thresholds return to normal levels - Deactivating safety systems...")
                
                if fire_devices["alarms"]:
                    logger.info(f"Deactivating {len(fire_devices['alarms'])} fire alarms")
                    await toggle_devices(fire_devices["alarms"], "status", "off", token)
                
                if fire_devices["sprinklers"]:
                    for room_id, sprinkler_ids in fire_devices["sprinklers"].items():
                        logger.info(f"Deactivating sprinklers in {room_id}")
                        await toggle_devices(sprinkler_ids, "status", "off", token)

                if fire_devices["doors"]:
                    logger.info(f"Locking {len(fire_devices['doors'])} doors")
                    await toggle_devices(fire_devices["doors"], "locked", True, token)
                    
    except Exception as e:
        logger.error(f"Error in update_readings: {e}")
    
    # Update previous state
    previous_threshold_state = threshold_state
    
    return SensorResponse(
        message="Readings updated",
        temperature=readings.temperature,
        smoke_level=readings.smoke_level,
        fire_active=threshold_state
    )


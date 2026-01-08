from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List
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

async def get_fire_safety_devices(token: str) -> Dict[str, List[str]]:
    """
    Gets all fire alarm and sprinkler devices from appliances service.
    """
    fire_devices = {
        "alarms": [],
        "sprinklers": []
    }

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
                device_type = device.get("type")
                if device_type == "fire_alarm":
                    fire_devices["alarms"].append(device_id)
                elif device_type == "sprinkler":
                    fire_devices["sprinklers"].append(device_id)
            
            logger.info(f"Fire safety devices discovered: {fire_devices}")
            return fire_devices

    except httpx.RequestError as e:
        logger.error(f"Appliances service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch devices: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error getting fire safety devices: {e}")
    
    return fire_devices

async def toggle_devices(device_ids: List[str], status: str, token: str):
    """
    Toggle devices on/off.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for device_id in device_ids:
            try:
                response = await client.post(
                    f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/updateState",
                    json={"state": "status", "value": status},
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

    # Only contact send request to appliance service if threshold state has changed
    if threshold_state != previous_threshold_state:
        
        # Extract token from request headers
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

        token = auth_header.removeprefix("Bearer ").strip()
        
        try:
            # Get fire safety devices
            fire_devices = await get_fire_safety_devices(token)
            
            if threshold_state:
                logger.warning("Thresholds exceeded! Activating safety systems...")
                
                # Activate alarms
                if fire_devices["alarms"]:
                    logger.info(f"Activating {len(fire_devices['alarms'])} fire alarms")
                    await toggle_devices(fire_devices["alarms"], "on", token)
                
                if fire_devices["sprinklers"]:
                    logger.info(f"Activating {len(fire_devices['sprinklers'])} sprinklers")
                    await toggle_devices(fire_devices["sprinklers"], "on", token)
                    
                if not fire_devices["alarms"] and not fire_devices["sprinklers"]:
                    logger.info("No fire devices found")
            else:
                logger.info("Thresholds normal. Deactivating safety systems...")
                
                # Deactivate alarms
                if fire_devices["alarms"]:
                    logger.info(f"Deactivating {len(fire_devices['alarms'])} fire alarms")
                    await toggle_devices(fire_devices["alarms"], "off", token)
                
                # Deactivate sprinklers
                if fire_devices["sprinklers"]:
                    logger.info(f"Deactivating {len(fire_devices['sprinklers'])} sprinklers")
                    await toggle_devices(fire_devices["sprinklers"], "off", token)
        
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


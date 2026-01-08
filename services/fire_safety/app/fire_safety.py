from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Union
from app.auth import verify_user
import httpx
import os

router = APIRouter()

class SensorReadings(BaseModel):
    temperature: float
    smoke_level: float

class SensorResponse(BaseModel):
    message: str
    temperature: float
    smoke_level: float
    fire_active: bool

TEMPERATURE_THRESHOLD = 75.0 
SMOKE_THRESHOLD = 0.3  

current_readings = {
    "temperature": 20.0,
    "smoke_level": 0.0
}

# Track previous threshold state
previous_threshold_state = False

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

async def get_fire_safety_devices(token: str):
    """Gets all fire alarm and sprinkler devices from appliances service"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch devices: {response.status_code}")
                return {"alarms": [], "sprinklers": [], "doors": []}
            
            devices = response.json()
            fire_devices = {
                "alarms": [],
                "sprinklers": [],
                "doors": []
            }
            
            for device_id, device in devices.items():
                device_type = device.get("type")
                if device_type == "fire_alarm":
                    fire_devices["alarms"].append(device_id)
                elif device_type == "sprinkler":
                    fire_devices["sprinklers"].append(device_id)
                elif device_type == "door":
                    fire_devices["doors"].append(device_id)
            
            print(f"Fire safety devices found: {fire_devices}")
            return fire_devices
    except Exception as e:
        print(f"Error getting fire safety devices: {e}")
        return {"alarms": [], "sprinklers": [], "doors": []}

async def toggle_devices(device_ids: list, state_name: str, value: Union[str, bool], token: str):
    """Toggles device states """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for device_id in device_ids:
                response = await client.post(
                    f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/updateState",
                    json={"state": state_name, "value": value},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
    except Exception as e:
        print(f"Error toggling device state: {e}")

@router.get("/readings", response_model=SensorReadings)
def get_readings(user = Depends(verify_user)):
    """Get current sensor readings"""
    return current_readings

@router.post("/readings", response_model=SensorResponse)
async def update_readings(readings: SensorReadings, request: Request, user = Depends(verify_user)):
    """Updates sensor readings and trigger alarms if thresholds exceeded"""
    global previous_threshold_state
    
    print(f"Sensor readings - Temperature: {readings.temperature}, Smoke: {readings.smoke_level}")
    
    current_readings["temperature"] = readings.temperature
    current_readings["smoke_level"] = readings.smoke_level
    
    # Check current threshold state
    threshold_state = readings.temperature > TEMPERATURE_THRESHOLD or readings.smoke_level > SMOKE_THRESHOLD

    # Only contact send request to appliance service if threshold state has changed
    if threshold_state != previous_threshold_state:
        
        # Extract token from request headers
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header else ""
        
        try:
            # Get fire safety devices
            fire_devices = await get_fire_safety_devices(token)
            
            if threshold_state:
                print("Thresholds exceeded! Activating safety systems...")
                
                # Activate alarms
                if fire_devices["alarms"]:
                    print(f"Activating {len(fire_devices['alarms'])} fire alarms")
                    await toggle_devices(fire_devices["alarms"], "status", "on", token)
                
                if fire_devices["sprinklers"]:
                    print(f"Activating {len(fire_devices['sprinklers'])} sprinklers")
                    await toggle_devices(fire_devices["sprinklers"], "status", "on", token)
                
                if fire_devices["doors"]:
                    print(f"Unlocking {len(fire_devices['doors'])} doors")
                    await toggle_devices(fire_devices["doors"], "locked", False, token)
                    
                if not fire_devices["alarms"] and not fire_devices["sprinklers"]:
                    print("No fire devices found")
            else:
                print("Thresholds normal. Deactivating safety systems...")
                
                # Deactivate alarms
                if fire_devices["alarms"]:
                    print(f"Deactivating {len(fire_devices['alarms'])} fire alarms")
                    await toggle_devices(fire_devices["alarms"], "status", "off", token)
                
                # Deactivate sprinklers
                if fire_devices["sprinklers"]:
                    print(f"Deactivating {len(fire_devices['sprinklers'])} sprinklers")
                    await toggle_devices(fire_devices["sprinklers"], "status", "off", token)

                if fire_devices["doors"]:
                    print(f"Locking {len(fire_devices['doors'])} doors")
                    await toggle_devices(fire_devices["doors"], "locked", True, token)
        except Exception as e:
            print(f"Error in update_readings: {e}")
        
        # Update previous state
        previous_threshold_state = threshold_state
    
    return SensorResponse(
        message="Readings updated",
        temperature=readings.temperature,
        smoke_level=readings.smoke_level,
        fire_active=threshold_state
    )


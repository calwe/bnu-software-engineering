from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user
import httpx
import os

router = APIRouter()

class OccupancyResponse(BaseModel):
    message: str

monitoring_device_states = {
    "motionSensors" : {},
    "cameras" : {}
}

RoomsOccupancy : Dict[str, bool] = {}

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

async def get_monitoring_devices(token: str):
    global monitoring_device_states
    """Gets all camera and motion sensor devices from appliances service"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch devices: {response.status_code}")
                return {"alarms": []}
            
            devices = response.json()
            
            # device_key is now the device ID
            for device_id, device in devices.items():
                device_type = device.get("type")
                if device_type == "motion_sensor":
                    monitoring_device_states["motionSensors"][device_id] = device
                    RoomsOccupancy[device["room"]] = False
                elif device_type == "camera":
                    monitoring_device_states["cameras"][device_id] = device
                    RoomsOccupancy[device["room"]] = False
            #print(f"Monitoring devices found: {monitoring_device_states}")
    except Exception as e:
        print(f"Error getting security devices: {e}")
        return {"alarms": []}

@router.post("/occupancy_check", response_model=OccupancyResponse)
async def check_occupancy(request: Request, user = Depends(verify_user)):
    # Extract token from request headers
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    try:
        # Get monitoring devices
        await get_monitoring_devices(token)
        securityAlert = False
        for device_id, device in monitoring_device_states["cameras"].items():
            RoomsOccupancy[device["room"]] = device["peopleDetected"]
        for device_id, device in monitoring_device_states["motionSensors"].items():
            RoomsOccupancy[device["room"]] = device["peopleDetected"]
    
    except Exception as e:
        print(f"Error in update_readings: {e}")
        
    return OccupancyResponse(
        message="Readings updated",
    )

@router.get("/", response_model=Dict[str, bool])
def get_occupancy(user = Depends(verify_user)):
    return RoomsOccupancy

@router.get("/{room}", response_model=Dict[str, bool])
def get_room_occupancy(room: str, user = Depends(verify_user)):
    if room not in RoomsOccupancy:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"occupied": RoomsOccupancy[room]}


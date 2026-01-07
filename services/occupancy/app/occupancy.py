from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user
import httpx
import os

router = APIRouter()

class OccupancyResponse(BaseModel):
    message: str

RoomsOccupancy : Dict[str, bool] = {}

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

async def get_monitoring_devices(token: str):
    """Gets all camera and motion sensor devices from appliances service"""
    try:
        monitoring_device_states = {}
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
                if device_type == "motion_sensor" or device_type == "camera":
                    monitoring_device_states[device_id] = device
                    #Populate the RoomsOccupancy dictionary of rooms - if a device is in a room
                    #not in the dictionary already, add it.
                    # if it is, set it to false so that it can be checked and updated in the check_occupany function
                    RoomsOccupancy[device["room"]] = False
        return monitoring_device_states
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
        monitoring_device_states = await get_monitoring_devices(token)
        for device_id, device in monitoring_device_states.items():
            # if any device detects people in room, set that room to occupied
            if (device["peopleDetected"]):
                RoomsOccupancy[device["room"]] = True
    
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


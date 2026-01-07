from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.auth import verify_user
import httpx
import os
import requests

router = APIRouter()

class SecurityResponse(BaseModel):
    message: str


current_security_device_states = {
    "motionSensors" : {},
    "cameras" : {}
}
RoomOccupied = {}

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

async def get_security_devices(token: str):
    """Gets all security alarm, camera and motion sensor devices from appliances service"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch devices: {response.status_code}")
                return {"alarms": [], "motionSensors": [], "cameras": []}
            
            devices = response.json()
            security_devices = {
                "alarms": [],
                "motionSensors": [],
                "cameras": []
            }
            
            # device_key is now the device ID
            for device_id, device in devices.items():
                device_type = device.get("type")
                if device_type == "security_alarm":
                    security_devices["alarms"].append(device_id)
                elif device_type == "motion_sensor":
                    current_security_device_states["motionSensors"][device_id] = device
                elif device_type == "camera":
                    current_security_device_states["cameras"][device_id] = device
            print(f"Security devices found: {security_devices}")
            return security_devices
    except Exception as e:
        print(f"Error getting security devices: {e}")
        return {"alarms": [], "motionSensors": [], "cameras": []}

async def toggle_devices(device_ids: list, status: str, token: str):
    """Toggle devices on/off"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for device_id in device_ids:
                response = await client.post(
                    f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/command",
                    json={"status": status},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
    except Exception as e:
        print(f"Error toggling device state: {e}")

@router.post("/security_check", response_model=SecurityResponse)
async def check_security(request: Request, user = Depends(verify_user)):
    # Extract token from request headers
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    try:
        # Get security devices
        security_devices = await get_security_devices(token)
        securityAlert = False
        for device_id, device in current_security_device_states["cameras"].items():
            if device.peopleSpotted:
                securityAlert = True
        for device_id, device in current_security_device_states["motionSensors"].items():
            if device.motionDetected:
                securityAlert = True

        if securityAlert:
            print("Security Alert! Activating alarms...")
            
            # Activate alarms
            if security_devices["alarms"]:
                print(f"Activating {len(security_devices['alarms'])} alarms")
                await toggle_devices(security_devices["alarms"], "on", token)
                
            if not security_devices["alarms"]:
                print("No security devices found")
        else:
            print("No security alert. Deactivating alarms...")
            
            # Deactivate alarms
            if security_devices["alarms"]:
                print(f"Deactivating {len(security_devices['alarms'])} alarms")
                await toggle_devices(security_devices["alarms"], "off", token)
        
    
    except Exception as e:
        print(f"Error in update_readings: {e}")
        

    return SecurityResponse(
        message="Readings updated",
    )


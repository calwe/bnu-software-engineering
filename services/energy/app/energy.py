from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List
from app.auth import verify_user
import httpx
import os

router = APIRouter()

LIGHT_POWER_RATING = 10.0
FIRE_ALARM_POWER_RATING = 5.0
SPRINKLER_POWER_RATING = 0.0
HEATER_POWER_RATING = 3.0

class RoomStatus(BaseModel):
    room_id: str
    room_name: str
    is_empty: bool

class EnergyResponse(BaseModel):
    message: str
    room_id: str
    room_name: str
    is_empty: bool
    lights_turned_on: bool
    lights_turned_off: bool
    light_names: List[str]

class PowerConsumption(BaseModel):
    total_consumption: float
    active_devices: int
    device_breakdown: Dict[str, float]

# Track room statuses
rooms = {
    "living_room": {"name": "Living Room", "is_empty": False},
    "bedroom": {"name": "Bedroom", "is_empty": False},
    "kitchen": {"name": "Kitchen", "is_empty": False},
}

# Track previous room states
previous_room_states = {room_id: False for room_id in rooms.keys()}

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

async def get_light_devices(token: str):
    """Gets all light devices from appliances service"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch devices: {response.status_code}")
                return {}
            
            devices = response.json()
            lights = {}
            
            for device_id, device in devices.items():
                device_type = device.get("type")
                if device_type == "light":
                    room = device.get("room", "unknown")
                    if room not in lights:
                        lights[room] = []
                    lights[room].append({
                        "id": device_id,
                        "name": device.get("name", device_id)
                    })
            
            return lights
    except Exception as e:
        print(f"Error getting devices: {e}")
        return {}

async def toggle_lights(light_devices: list, status: str, token: str):
    """Toggle lights on/off"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for light in light_devices:
                device_id = light["id"]
                response = await client.post(
                    f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/updateState",
                    json={"state": "status", "value": status},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
    except Exception as e:
        print(f"Error toggling lights: {e}")

async def get_power_consumption(token: str):
    """Gets power consumption data from all appliances"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch devices: {response.status_code}")
                return {"total": 0.0, "active": 0, "breakdown": {}}
            
            devices = response.json()
            total_consumption = 0.0
            active_count = 0
            breakdown = {}
            
            power_ratings = {
                "light": LIGHT_POWER_RATING,      
                "fire_alarm": FIRE_ALARM_POWER_RATING, 
                "sprinkler": SPRINKLER_POWER_RATING,
                "heater": HEATER_POWER_RATING
            }
            
            for device_id, device in devices.items():
                device_type = device.get("type", "unknown")
                if device_type == "sprinkler" or device_type == "door":
                    continue
                status = device.get("states").get("status", "off")
                device_name = device.get("name", device_id)
    
                power_rating = power_ratings.get(device_type, 0.0)
                
                if status == "on":
                    total_consumption += power_rating
                    active_count += 1
                    breakdown[device_name] = power_rating
                else:
                    breakdown[device_name] = 0.0
            
            return {
                "total": total_consumption,
                "active": active_count,
                "breakdown": breakdown
            }
    except Exception as e:
        print(f"Error getting power consumption: {e}")
        return {"total": 0.0, "active": 0, "breakdown": {}}

@router.get("/rooms")
def get_rooms(user = Depends(verify_user)):
    """Get all rooms and their status"""
    return rooms

@router.get("/consumption")
async def get_consumption(request: Request, user = Depends(verify_user)):
    """Get current power consumption"""
    # Extract token from request headers
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    consumption_data = await get_power_consumption(token)
    
    return PowerConsumption(
        total_consumption=consumption_data["total"],
        active_devices=consumption_data["active"],
        device_breakdown=consumption_data["breakdown"]
    )

@router.post("/room-status", response_model=EnergyResponse)
async def update_room_status(status: RoomStatus, request: Request, user = Depends(verify_user)):
    """Updates room empty status and automatically controls lights"""
    global previous_room_states
    
    room_id = status.room_id
    
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    print(f"Room status update - Room: {status.room_name}, Empty: {status.is_empty}")
    
    # Update room status
    rooms[room_id]["is_empty"] = status.is_empty
    
    lights_turned_on = False
    lights_turned_off = False
    controlled_light_names = []
    
    # Check if room state has changed
    state_changed = previous_room_states.get(room_id, False) != status.is_empty
    
    # Only contact appliance service if room state has changed
    if state_changed:
        # Extract token from request headers
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header else ""
        
        try:
            # Get light devices organized by room
            light_devices = await get_light_devices(token)
            
            if status.is_empty:
                print(f"No presence detected in {status.room_name}. Turning off lights...")

                # Turn off lights in this room
                room_lights = light_devices.get(room_id, [])
                if room_lights:
                    print(f"Turning off {len(room_lights)} lights in {status.room_name}")
                    await toggle_lights(room_lights, "off", token)
                    lights_turned_off = True
                    controlled_light_names = [light["name"] for light in room_lights]
                    
                if not room_lights:
                    print(f"No lights found in {status.room_name}")
            else:
                print(f"Presence detected in {status.room_name}. Turning on lights...")
                
                # Turn on lights in this room
                room_lights = light_devices.get(room_id, [])
                if room_lights:
                    print(f"Turning on {len(room_lights)} lights in {status.room_name}")
                    await toggle_lights(room_lights, "on", token)
                    lights_turned_on = True
                    controlled_light_names = [light["name"] for light in room_lights]
        
        except Exception as e:
            print(f"Error in update_room_status: {e}")
        
        # Update previous state
        previous_room_states[room_id] = status.is_empty
    
    return EnergyResponse(
        message="Room devices status updated",
        room_id=room_id,
        room_name=status.room_name,
        is_empty=status.is_empty,
        lights_turned_on=lights_turned_on,
        lights_turned_off=lights_turned_off,
        light_names=controlled_light_names
    )

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
OCCUPANCY_SERVICE_URL = "http://occupancy:8000"

print(f"Appliances Service URL: {APPLIANCES_SERVICE_URL}")  
print(f"Occupancy Service URL: {OCCUPANCY_SERVICE_URL}")

async def get_occupancy_data(token: str):
    """Gets occupancy data from occupancy service"""
    try:
        print(f"Occupancy Service URL: {OCCUPANCY_SERVICE_URL}")

        print(f"Appliances Service URL: {APPLIANCES_SERVICE_URL}")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{OCCUPANCY_SERVICE_URL}/occupancy/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            if response.status_code != 200:
                print(f"Failed to fetch occupancy: {response.status_code}")
                return {}
            
            return response.json()
    except Exception as e:
        print(f"Error getting occupancy data: {e}")
        return {}

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
                    lights[room].append(device_id)
            
            print(f"Light devices found: {lights}")
            return lights
    except Exception as e:
        print(f"Error getting devices: {e}")
        return {}

async def toggle_lights(device_ids: list, status: str, token: str):
    """Toggle lights on/off"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for device_id in device_ids:
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

@router.post("/auto-control")
async def auto_control(request: Request, user = Depends(verify_user)):
    """Automatically control lights based on occupancy"""
    global previous_room_states
    
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    occupancy_data = await get_occupancy_data(token)
    
    light_devices = await get_light_devices(token)
    
    changes = []
    
    for room_id, room_info in rooms.items():
        is_occupied = occupancy_data.get(room_id, False)
        room_info["is_empty"] = not is_occupied
        
        # Only process if occupancy state has changed
        if is_occupied != previous_room_states[room_id]:

            room_lights = light_devices.get(room_id, [])
            
            if room_lights:
                try:
                    if is_occupied:
                        print(f"{room_info['name']} is occupied. Turning on {len(room_lights)} lights...")
                        await toggle_lights(room_lights, "on", token)
                        changes.append({
                            "room": room_info["name"],
                            "status": "on",
                            "lights": len(room_lights)
                        })
                    else:
                        print(f"{room_info['name']} is empty. Turning off {len(room_lights)} lights...")
                        await toggle_lights(room_lights, "off", token)
                        changes.append({
                            "room": room_info["name"],
                            "status": "off",
                            "lights": len(room_lights)
                        })
                except Exception as e:
                    print(f"Error controlling lights in {room_info['name']}: {e}")
            
            previous_room_states[room_id] = is_occupied
    
    return {"changes": changes}

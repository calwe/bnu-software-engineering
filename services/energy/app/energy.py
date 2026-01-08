from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List
from app.auth import verify_user
import httpx
import os
import logging

router = APIRouter()
logger = logging.getLogger("energy_service")

# ===============================
# Configuration
# ===============================

LIGHT_POWER_RATING = 10.0
FIRE_ALARM_POWER_RATING = 5.0
SPRINKLER_POWER_RATING = 0.0
HEATER_POWER_RATING = 3.0

APPLIANCES_SERVICE_URL = os.getenv("APPLIANCES_SERVICE_URL", "http://appliances:8000")

# ===============================
# Models
# ===============================

class RoomStatus(BaseModel):
    """
    Represents the occupancy status of a room.
    """
    room_id: str
    room_name: str
    is_empty: bool

class EnergyResponse(BaseModel):
    """
    Response returned after automatically controlling room devices.
    """
    message: str
    room_id: str
    room_name: str
    is_empty: bool
    lights_turned_on: bool
    lights_turned_off: bool
    light_names: List[str]

class PowerConsumption(BaseModel):
    """
    Current power consumption summary.
    """
    total_consumption: float
    active_devices: int
    device_breakdown: Dict[str, float]

# ===============================
# State
# ===============================

# Track room statuses
rooms: Dict[str, Dict[str, bool]] = {
    "living_room": {"name": "Living Room", "is_empty": False},
    "bedroom": {"name": "Bedroom", "is_empty": False},
    "kitchen": {"name": "Kitchen", "is_empty": False},
}

# Track previous room states
previous_room_states: Dict[str, bool] = {room_id: False for room_id in rooms.keys()}

# ===============================
# Helper functions
# ===============================

async def get_light_devices(token: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Gets all light devices from appliances service.
    """
    lights_by_room: Dict[str, List[Dict[str, str]]] = {}

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
                if device_type == "light":
                    room = device.get("room", "unknown")
                    lights_by_room.setdefault(room, []).append({
                        "id": device_id,
                        "name": device.get("name", device_id)
                    })

            return lights_by_room

    except httpx.RequestError as e:
        logger.error(f"Appliances service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch devices: {e.response.status_code}")
    except Exception as e:
        print(f"Error getting devices: {e}")
        
    return lights_by_room

async def toggle_lights(light_devices: List[Dict[str, str]], status: str, token: str):
    """
    Toggle lights on/off.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for light in light_devices:
            try:
                response = await client.post(
                    f"{APPLIANCES_SERVICE_URL}/appliances/{device_id}/updateState",
                    json={"state": "status", "value": status},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning(
                    f"Failed to toggle light '{light['id']}': {e}"
                )

async def get_power_consumption(token: str)  -> Dict[str, object]:
    """
    Gets power consumption data from all appliances.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )

            response.raise_for_status()
            devices = response.json()

            total_consumption = 0.0
            active_count = 0
            breakdown: Dict[str, float] = {}
            
            power_ratings = {
                "light": LIGHT_POWER_RATING,      
                "fire_alarm": FIRE_ALARM_POWER_RATING, 
                "sprinkler": SPRINKLER_POWER_RATING,
                "heater": HEATER_POWER_RATING
            }
            
            # device_id is now the dictionary key
            for device_id, device in devices.items():
                device_type = device.get("type", "unknown")

                if device_type == "sprinkler":
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
    except httpx.RequestError as e:
        logger.error(f"Appliances service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch devices: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error getting power consumption: {e}")
        
    return {"total": 0.0, "active": 0, "breakdown": {}}

# ===============================
# API endpoints
# ===============================

@router.get("/rooms")
def get_rooms(user = Depends(verify_user)):
    """
    Get all rooms and their status.
    """
    return rooms

@router.get("/consumption", response_model=PowerConsumption)
async def get_consumption(request: Request, user = Depends(verify_user)):
    """
    Get current power consumption.
    """
    # Extract token from request headers
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    token = auth_header.removeprefix("Bearer ").strip()
    
    consumption_data = await get_power_consumption(token)
    
    return PowerConsumption(
        total_consumption=consumption_data["total"],
        active_devices=consumption_data["active"],
        device_breakdown=consumption_data["breakdown"]
    )

#I will change this when we get the occupancy service
@router.post("/room-status", response_model=EnergyResponse)
async def update_room_status(status: RoomStatus, request: Request, user = Depends(verify_user)):
    """
    Updates room empty status and automatically controls lights.
    """
    global previous_room_states
    
    room_id = status.room_id
    
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    logger.info(
        f"Room update received: "
        f"{status.room_name}, empty={status.is_empty}"
    )
    
    # Update room status
    rooms[room_id]["is_empty"] = status.is_empty
    
    lights_turned_on = False
    lights_turned_off = False
    controlled_light_names: List[str] = []
    
    # Check if room state has changed
    state_changed = previous_room_states.get(room_id, False) != status.is_empty
    
    # Only contact appliance service if room state has changed
    if state_changed:
        # Extract token from request headers
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid Authorization header"
            )

        token = auth_header.removeprefix("Bearer ").strip()

        light_devices = await get_light_devices(token)
        room_lights = light_devices.get(room_id, [])
        
        if status.is_empty:
            logger.info(f"No presence detected in {status.room_name}. Turning off lights...")

            # Turn off lights in this room
            if room_lights:
                logger.info(f"Turning off {len(room_lights)} lights in {status.room_name}")
                await toggle_lights(room_lights, "off", token)
                lights_turned_off = True
                controlled_light_names = [light["name"] for light in room_lights]
                
            if not room_lights:
                logger.info(f"No lights found in {status.room_name}")
        else:
            logger.info(f"Presence detected in {status.room_name}. Turning on lights...")
            
            # Turn on lights in this room
            room_lights = light_devices.get(room_id, [])
            if room_lights:
                logger.info(f"Turning on {len(room_lights)} lights in {status.room_name}")
                await toggle_lights(room_lights, "on", token)
                lights_turned_on = True
                controlled_light_names = [light["name"] for light in room_lights]
        
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

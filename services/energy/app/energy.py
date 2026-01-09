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
OCCUPANCY_SERVICE_URL = "http://occupancy:8000"

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

async def get_occupancy_data(token: str):
    """
    Gets occupancy data from occupancy service.
    """
    try:
        logger.info(f"Occupancy Service URL: {OCCUPANCY_SERVICE_URL}")

        logger.info(f"Appliances Service URL: {APPLIANCES_SERVICE_URL}")
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

async def get_light_devices(token: str) -> Dict[str, List[str]]:
    """
    Gets all light devices grouped by room.
    """
    lights_by_room: Dict[str, List[str]] = {}

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(
                f"{APPLIANCES_SERVICE_URL}/appliances/",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

            devices = response.json()

            for device_id, device in devices.items():
                if device.get("type") == "light":
                    room = device.get("room")
                    if not room:
                        logger.warning(f"Light {device_id} has no room assigned")
                        continue

                    lights_by_room.setdefault(room, []).append(device_id)

            logger.info(f"Light devices found: {lights_by_room}")
            return lights_by_room

    except httpx.RequestError as e:
        logger.error(f"Appliances service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch devices: {e.response.status_code}")
    except Exception:
        logger.exception("Unexpected error in get_light_devices")

    return {}


async def toggle_lights(device_ids: list, status: str, token: str):
    """
    Toggle lights on/off.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for device_id in device_ids:
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

@router.post("/auto-control")
async def auto_control(request: Request, user = Depends(verify_user)):
    """
    Automatically control lights based on occupancy.
    """
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
                        logger.info(f"{room_info['name']} is occupied. Turning on {len(room_lights)} lights...")
                        await toggle_lights(room_lights, "on", token)
                        changes.append({
                            "room": room_info["name"],
                            "status": "on",
                            "lights": len(room_lights)
                        })
                    else:
                        logger.info(f"{room_info['name']} is empty. Turning off {len(room_lights)} lights...")
                        await toggle_lights(room_lights, "off", token)
                        changes.append({
                            "room": room_info["name"],
                            "status": "off",
                            "lights": len(room_lights)
                        })
                except Exception as e:
                    logger.error(f"Error controlling lights in {room_info['name']}: {e}")
            
            previous_room_states[room_id] = is_occupied
    
    return {"changes": changes}

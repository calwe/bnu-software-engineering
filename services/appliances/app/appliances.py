from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.auth import verify_user

router = APIRouter()

# ===============================
# Pydantic models
# ===============================

class Device(BaseModel):
    """
    Represents the current state of a smart home device.
    Fields are optional because different device types support different capabilities.
    """
    name: str
    type: str
    room: Optional[str] = None
    status: Optional[str] = None
    temperature: Optional[int] = None
    locked: Optional[bool] = None

class DeviceCommand(BaseModel):
    """
    Represents a command sent to a device.
    Only provided fields will be updated.
    """
    status: Optional[str] = None
    temperature: Optional[int] = None
    locked: Optional[bool] = None

class CommandResponse(BaseModel):
    """
    Response returned after successfully applying a command.
    """
    message: str
    device: str
    new_state: Device

class FireSafetyTrigger(BaseModel):
    activate: bool

# ===============================
# Device store
# This acts as a mock database for demonstration purposes.
# ===============================

devices: Dict[str, Dict[str, Any]] = {
    "light1": {"name": "Living Room Main Light", "type": "light", "room": "living_room", "status": "off"},
    "light2": {"name": "Living Room Lamp", "type": "light", "room": "living_room", "status": "off"},
    "light3": {"name": "Bedroom Ceiling Light", "type": "light", "room": "bedroom", "status": "off"},
    "light4": {"name": "Bedroom Bedside Lamp", "type": "light", "room": "bedroom", "status": "off"},
    "light5": {"name": "Kitchen Main Light", "type": "light", "room": "kitchen", "status": "off"},
    "light6": {"name": "Kitchen Counter Light", "type": "light", "room": "kitchen", "status": "off"},
    "heater1": {"name": "Living Room Heater", "type": "heater", "room": "living_room", "temperature": 20},
    "door1": {"name": "Front Door", "type": "door", "locked": True},
    "fire_alarm1": {"name": "Living Room Fire Alarm", "type": "fire_alarm", "room": "living_room", "status": "off"},
    "sprinkler1": {"name": "Living Room Sprinkler", "type": "sprinkler", "room": "living_room", "status": "off"},
}

# ===============================
# API endpoints
# ===============================

@router.get("/", response_model=Dict[str, Device])
def list_devices(user = Depends(verify_user)):
    """
    Returns all registered devices with their current states.
    """
    return devices

@router.get("/{device_id}", response_model=Device)
def get_device(device_id: str, user = Depends(verify_user)):
    """
    Retrieves the state of a single device.
    """
    device = devices.get(device_id)

    if device_id is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Device {device_id} not found"
            )

    return device 

@router.post("/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: DeviceCommand, user = Depends(verify_user)):
    """
    Applies a command to a device by updating only the provided fields.
    """
    device = devices.get(device_id)

    if device_id is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Device {device_id} not found"
            )

    command_data = command.dict(exclude_none=True)

    if not command_data:
        raise HTTPException(
            status_code=400,
            detail="No valid command fields provided"
        )

    device_type = device.get("type")

    if device_type == "light" and "temperature" in command_data:
        raise HTTPException(
            status_code=400,
            detail="Lights do not support temperature control"
        )

    if device_type == "heater" and "locked" in command_data:
        raise HTTPException(
            status_code=400,
            detail="Heaters do not support locking"
        )

    device.update(command_data)

    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=device
    )

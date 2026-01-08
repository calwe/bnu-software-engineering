from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user

router = APIRouter()

class Device(BaseModel):
    name: str
    type: str
    room: Optional[str] = None
    status: Optional[str] = None
    temperature: Optional[int] = None
    locked: Optional[bool] = None

class DeviceCommand(BaseModel):
    status: Optional[str] = None
    temperature: Optional[int] = None
    locked: Optional[bool] = None

class CommandResponse(BaseModel):
    message: str
    device: str
    new_state: Device

class FireSafetyTrigger(BaseModel):
    activate: bool

devices: Dict[str, dict] = {
    "light1": {"name": "Living Room Main Light", "type": "light", "room": "living_room", "status": "off"},
    "light2": {"name": "Living Room Lamp", "type": "light", "room": "living_room", "status": "off"},
    "light3": {"name": "Bedroom Ceiling Light", "type": "light", "room": "bedroom", "status": "off"},
    "light4": {"name": "Bedroom Bedside Lamp", "type": "light", "room": "bedroom", "status": "off"},
    "light5": {"name": "Kitchen Main Light", "type": "light", "room": "kitchen", "status": "off"},
    "light6": {"name": "Kitchen Counter Light", "type": "light", "room": "kitchen", "status": "off"},
    "heater1": {"name": "Living Room Heater", "type": "heater", "room": "living_room", "temperature": 20},
    "door1": {"name": "Front Door", "type": "door", "status": "locked"},
    "fire_alarm1": {"name": "Living Room Fire Alarm", "type": "fire_alarm", "room": "living_room", "status": "off"},
    "sprinkler1": {"name": "Living Room Sprinkler", "type": "sprinkler", "room": "living_room", "status": "off"},
}

@router.get("/", response_model=Dict[str, Device])
def list_devices(user = Depends(verify_user)):
    return devices

@router.get("/{device_id}", response_model=Device)
def get_device(device_id: str, user = Depends(verify_user)):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@router.post("/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: DeviceCommand, user = Depends(verify_user)):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_name = devices[device_id].get("name", device_id)
    
    print(f"Received command for {device_id} ({device_name}): {command.dict(exclude_none=True)}")
    devices[device_id].update(command.dict(exclude_none=True))
    print(f"Updated device state: {devices[device_id]}")
    
    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=devices[device_id]
    )

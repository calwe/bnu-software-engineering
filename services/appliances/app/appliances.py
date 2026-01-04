from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user

router = APIRouter()

class Device(BaseModel):
    id: Optional[str] = None
    type: str
    room: Optional[str] = None
    status: Optional[str] = None
    temperature: Optional[int] = None
    locked: Optional[bool] = None
    alarm_active: Optional[bool] = None
    sprinkler_active: Optional[bool] = None

class DeviceCommand(BaseModel):
    status: Optional[str] = None
    temperature: Optional[int] = None
    locked: Optional[bool] = None
    alarm_active: Optional[bool] = None
    sprinkler_active: Optional[bool] = None

class CommandResponse(BaseModel):
    message: str
    device: str
    new_state: Device

class FireSafetyTrigger(BaseModel):
    activate: bool

devices: Dict[str, dict] = {
    
    "Living Room Main Light": {"id": "light1", "type": "light", "room": "living_room", "status": "off"},
    "Living Room Lamp": {"id": "light2", "type": "light", "room": "living_room", "status": "off"},
    "Bedroom Ceiling Light": {"id": "light3", "type": "light", "room": "bedroom", "status": "off"},
    "Bedroom Bedside Lamp": {"id": "light4", "type": "light", "room": "bedroom", "status": "off"},
    "Kitchen Main Light": {"id": "light5", "type": "light", "room": "kitchen", "status": "off"},
    "Kitchen Counter Light": {"id": "light6", "type": "light", "room": "kitchen", "status": "off"},
    "Living Room Heater": {"id": "heater1", "type": "heater", "room": "living_room", "temperature": 20},
    "Front Door": {"id": "door1", "type": "door", "locked": True},
    "Living Room Fire Alarm": {"id": "fire_alarm1", "type": "fire_alarm", "room": "living_room", "fire_alarm_active": False, "status": "off"},
    "Living Room Sprinkler": {"id": "sprinkler1", "type": "sprinkler", "room": "living_room", "sprinkler_active": False, "status": "off"},
}

@router.get("/", response_model=Dict[str, Device])
def list_devices(user = Depends(verify_user)):
    return devices

@router.post("/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: DeviceCommand, user = Depends(verify_user)):
    device_name = None
    for name, device in devices.items():
        if device.get("id") == device_id:
            device_name = name
            break
    
    if device_name is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    print(f"Received command for {device_id} ({device_name}): {command.dict(exclude_none=True)}")
    devices[device_name].update(command.dict(exclude_none=True))
    print(f"Updated device state: {devices[device_name]}")
    
    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=devices[device_name]
    )

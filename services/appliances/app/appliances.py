from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user

router = APIRouter()

class Device(BaseModel):
    type: str
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
    "light1": {"type": "light", "status": "off"},
    "heater1": {"type": "heater", "temperature": 20},
    "door1": {"type": "door", "locked": True},
    "fire_alarm1": {"type": "fire_alarm", "fire_alarm_active": False, "status": "off"},
    "sprinkler1": {"type": "sprinkler", "sprinkler_active": False, "status": "off"},
}

@router.get("/", response_model=Dict[str, Device])
def list_devices(user = Depends(verify_user)):
    return devices

@router.post("/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: DeviceCommand, user = Depends(verify_user)):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    print(f"Received command for {device_id}: {command.dict(exclude_none=True)}")
    devices[device_id].update(command.dict(exclude_none=True))
    print(f"Updated device state: {devices[device_id]}")
    
    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=devices[device_id]
    )

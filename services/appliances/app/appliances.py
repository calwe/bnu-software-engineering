from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user

router = APIRouter()

class Device(BaseModel):
    type: str
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

devices: Dict[str, dict] = {
    "light1": {"type": "light", "status": "off"},
    "heater1": {"type": "heater", "temperature": 20},
    "door1": {"type": "door", "locked": True},
}

@router.get("/", response_model=Dict[str, Device])
def list_devices(user = Depends(verify_user)):
    return devices

@router.post("/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: DeviceCommand, user = Depends(verify_user)):

    devices[device_id].update(command.dict(exclude_none=True))

    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=devices[device_id]
    )

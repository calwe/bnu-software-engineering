from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user
from app.devices import Device, StateValue, Light, Heater, Door, FireAlarm, Sprinkler

router = APIRouter()

devices: Dict[str, Device] = {
    "light1": Light(name = "Living Room Main Light", room = "living_room"),
    "light2": Light(name = "Living Room Lamp", room = "living_room"),
    "light3": Light(name = "Bedroom Ceiling Light", room = "bedroom"),
    "light4": Light(name = "Bedroom Bedside Lamp", room = "bedroom"),
    "light5": Light(name = "Kitchen Main Light", room = "kitchen"),
    "light6": Light(name = "Kitchen Counter Light", room = "kitchen"),
    "heater1": Heater(name = "Living Room Heater", room = "living_room"),
    "door1": Door(name = "Front Door"),
    "fire_alarm1": FireAlarm(name = "Living Room Fire Alarm", room = "living_room"),
    "sprinkler1": Sprinkler(name = "Living Room Sprinkler", room = "living_room"),
}

class UpdateStateRequest(BaseModel):
    state: str
    value: StateValue

@router.get("/", response_model=Dict[str, Device])
def list_devices(user = Depends(verify_user)):
    return devices

@router.get("/{device_id}", response_model=Device)
def get_device(device_id: str, user = Depends(verify_user)):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@router.post("/{device_id}/updateState", response_model=StateValue)
def update_state(device_id: str, request: UpdateStateRequest, user = Depends(verify_user)):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    device = devices[device_id]

    if request.state not in device.states:
        raise HTTPException(status_code=404, detail="State not found")
    
    device_name = devices[device_id].name

    print(f"Setting '{request.state}'='{request.value}' for {device_id} ({device_name})")
    old_state = device.states[request.state]
    device.states[request.state] = request.value
    
    return old_state

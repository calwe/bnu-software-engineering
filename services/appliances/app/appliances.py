from fastapi import APIRouter, Depends
from app.auth import verify_user

router = APIRouter()

devices = {
    "light1": {"type": "light", "status": "off"},
    "heater1": {"type": "heater", "temperature": 20},
    "door1": {"type": "door", "locked": True},
}

@router.get("/")
def list_devices(user = Depends(verify_user)):
    return devices

@router.post("/{device_id}/command")
def send_command(device_id: str, command: dict, user = Depends(verify_user)):

    devices[device_id].update(command)

    return {
        "message": "Command accepted",
        "device": device_id,
        "new_state": devices[device_id],
    }

from fastapi import APIRouter, Depends
from app.auth import verify_user

router = APIRouter()

devices = [
    {"id": "light1", "status": "off", "type": "light"},
    {"id": "heater1", "temperature": 20, "type": "heater"},
    {"id": "door1", "locked": True, "type": "door"},
]

@router.get("/")
def list_devices(user = Depends(verify_user)):
    return devices

@router.post("/{device_id}/command")
def send_command(device_id: str, command: dict, user = Depends(verify_user)):
    if device_id not in devices:
        return {"error": "Device not found"}

    devices[device_id].update(command)

    return {
        "message": "Command accepted",
        "device": device_id,
        "new_state": devices[device_id],
    }

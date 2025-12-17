from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user

router = APIRouter()

class SecurityDevice(BaseModel):
    enabled: bool = True

class Camera(SecurityDevice):
    videoData: str = ""

class MotionSensor(SecurityDevice):
    motionDetected: bool = False

class SecurityScheduleEntry(BaseModel):
    time: str = ""
    turnOn: bool = True
    devicesToAffect: list[SecurityDevice] = []

    
cameras: Dict[str, dict] = {
    "0": {"enabled": True, "videoData": ""},
    "1": {"enabled": True, "videoData": ""},
    "2": {"enabled": True, "videoData": ""},
}

motionSensors: Dict[str, dict] = {
    "0": {"enabled": True, "motionDetected": False},
    "1": {"enabled": True, "motionDetected": False},
    "2": {"enabled": True, "motionDetected": False},
}

@router.get("/cameras", response_model=Dict[str, Camera])
def getCameras(user = Depends(verify_user)):
    return cameras


@router.get("/motionSensors", response_model=Dict[str, MotionSensor])
def getMotionSensors(user = Depends(verify_user)):
    return motionSensors

class CommandResponse(BaseModel):
    message: str
    device: str
    new_state: SecurityDevice

class DeviceCommand(BaseModel):
    enabled: Optional[bool] = None

class CameraCommand(DeviceCommand):
    videoData: Optional[str] = None

class MotionSensorCommand(DeviceCommand):
    motionDetected: Optional[bool] = None


@router.post("/cameras/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: CameraCommand, user = Depends(verify_user)):
    cameras[device_id].update(command.dict(exclude_none=True))
    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=cameras[device_id]
    )

@router.post("/motionSensors/{device_id}/command", response_model=CommandResponse)
def send_command(device_id: str, command: MotionSensorCommand, user = Depends(verify_user)):
    motionSensors[device_id].update(command.dict(exclude_none=True))
    return CommandResponse(
        message="Command accepted",
        device=device_id,
        new_state=motionSensors[device_id]
    )


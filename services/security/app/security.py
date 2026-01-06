from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from app.auth import verify_user
import json

class SecurityDevice():
    def __init__(self, enabled=True):
        self.enabled = enabled

class Camera(SecurityDevice):
    def __init__(self, enabled=True, videoData = ""):
        super().__init__(enabled)
        self.videoData = videoData

class MotionSensor(SecurityDevice):
    def __init__(self, enabled=True, motionDetected=False):
        super().__init__(enabled)
        self.motionDetected = motionDetected  


cameras = [Camera(True, ""), Camera(True, ""), Camera(True, "")]
camerasDict = {}
for cam in cameras:
    camerasDict[id(cam)] = cam

motionSensors = [MotionSensor(True, False), MotionSensor(True, False), MotionSensor(True, False)]
motionSensorsDict = {}
for motionSensor in motionSensors:
    motionSensorsDict[id(motionSensor)] = motionSensor

schedule = [SecurityScheduleEntry("20:00", True, [])]

router = APIRouter()

def obj_dict(obj):
    return obj.__dict__

class DeviceCommand(BaseModel):
    enabled: Optional[bool] = None

class CameraCommand(DeviceCommand):
    videoData: Optional[str] = None

class MotionSensorCommand(DeviceCommand):
    motionDetected: Optional[bool] = None

@router.get("/")
async def getSecurity(user = Depends(verify_user)):
    return {
        "message":json.dumps(
        {
            "cameras":camerasDict,
            "motionSensors":motionSensorsDict
        }, default=obj_dict)            
    }

@router.post("/cameras/{device_id}/command")
def send_command(device_id: str, command: CameraCommand, user = Depends(verify_user)):
    camerasDict[int(device_id)].__dict__.update(command.dict(exclude_none=True))
    return {
        "message":json.dumps(
        {
            "cameras":camerasDict,
            "motionSensors":motionSensorsDict
        }, default=obj_dict)            
    }

@router.post("/motionSensors/{device_id}/command")
def send_command(device_id: str, command: MotionSensorCommand, user = Depends(verify_user)):
    motionSensorsDict[int(device_id)].__dict__.update(command.dict(exclude_none=True))
    return {
        "message":json.dumps(
        {
            "cameras":camerasDict,
            "motionSensors":motionSensorsDict
        }, default=obj_dict)            
    }



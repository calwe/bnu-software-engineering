from pydantic import BaseModel
from typing import Optional, Dict, Union

type StateValue = Union[str, int, float, bool]

class Device(BaseModel):
    name: str
    type: str
    room: Optional[str] = None
    states: Dict[str, StateValue]

class Light(Device):
    type: str = "light"
    states: Dict[str, StateValue] = { "status": "off" }

class Heater(Device):
    type: str = "heater"
    states: Dict[str, StateValue] = { "status": "off", "temperature": 20 }

class Door(Device):
    type: str = "door"
    states: Dict[str, StateValue] = { "locked": True }

class FireAlarm(Device):
    type: str = "fire_alarm"
    states: Dict[str, StateValue] = { "status": "off" }

class Sprinkler(Device):
    type: str = "sprinkler"
    states: Dict[str, StateValue] = { "status": "off" }

class Camera(Device):
    type: str = "camera"
    states: Dict[str, StateValue] = { "status": "off", "peopleDetected": False }

class MotionSensor(Device):
    type: str = "motion_sensor"
    states: Dict[str, StateValue] = { "status": "off", "peopleDetected": False }

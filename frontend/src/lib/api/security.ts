import { securityApi } from "./client";

export interface SecurityDevice {
  enabled: boolean;
}

export interface Camera extends SecurityDevice {
  videoData: string;
}

export interface MotionSensor extends SecurityDevice{
  motionDetected: boolean;
}

export interface SecurityScheduleEntry {
  time: string;
  turnOn: boolean;
  devicesToAffect: SecurityDevice[];
}

export const getCameras = async (): Promise<Record<string, Camera>> => {
  const result = await securityApi.get<Record<string, Camera>>("/security/cameras");
  return result.data;
};

export const getMotionSensors = async (): Promise<Record<string, MotionSensor>> => {
  const result = await securityApi.get<Record<string, MotionSensor>>("/security/motionSensors");
  return result.data;
};

export const sendCommand = async (target: string, index: string, command: Record<string, any>) => {
  const result = await securityApi.post("/security/" + target + "/" + index + "/command", command)
  return result.data
}

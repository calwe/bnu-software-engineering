import { Device } from "./appliances";
import { securityApi } from "./client";

export interface SensorReadings {
  temperature: number;
  smoke_level: number;
}

export interface SensorResponse {
  message: string;
  temperature: number;
  smoke_level: number;
  fire_active: boolean;
}

export const getDoors = async (): Promise<Record<string, Device>> => {
  const result = await securityApi.get<Record<string, Device>>("/security/doors");
  return result.data;
};

export const lockDoor = async (door: string) => {
  await securityApi.post(`/security/${door}/lock`);
};

export const unlockDoor = async (door: string) => {
  await securityApi.post(`/security/${door}/unlock`);
};

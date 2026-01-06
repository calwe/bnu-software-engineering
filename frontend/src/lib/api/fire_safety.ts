import { fireSafetyApi } from "./client";

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

export const getSensorReadings = async (): Promise<SensorReadings> => {
  const result = await fireSafetyApi.get<SensorReadings>("/fire_safety/readings");
  return result.data;
};

export const updateSensorReadings = async (readings: SensorReadings): Promise<SensorResponse> => {
  const result = await fireSafetyApi.post<SensorResponse>("/fire_safety/readings", readings);
  return result.data;
};
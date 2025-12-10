import { appliancesApi } from "./client";

export interface Device {
  id: string;
  type: string;
  status?: string;
  temperature?: number;
  locked?: boolean;
}

export const listDevices = async (): Promise<Record<string, Device>> => {
  const result = await appliancesApi.get<Record<string, Device>>("/appliances");
  return result.data;
};

export const sendCommand = async (deviceId: string, command: Record<string, any>) => {
  const result = await appliancesApi.post(`appliances/${deviceId}/command`, command)
  return result.data
}

import { appliancesApi } from "./client";

export interface Device {
  id: string;
  type: string;
  status?: string;
  temperature?: number;
  locked?: boolean;
}

// Make different types for light heater door etc. ??

export const listDevices = async (): Promise<Device[]> => {
  const result = await appliancesApi.get<Device[]>("/appliances")
  return result.data
}

export const sendCommand = async (deviceId: string, command: Record<string, any>) => {
  const result = await appliancesApi.post(`appliances/${deviceId}/command`, command)
  return result.data
}

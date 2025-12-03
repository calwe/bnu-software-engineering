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
  const res = await appliancesApi.get<Device[]>("/appliances")
  return res.data
}

export const sendCommand = async (deviceId: string, command: Record<string, any>) => {
  const res = await appliancesApi.post(`/${deviceId}/command`, command)
  return res.data
}

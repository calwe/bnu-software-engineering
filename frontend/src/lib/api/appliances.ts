import { appliancesApi } from "./client";

export type StateValue = string | number | boolean;

export interface Device {
  name: string;
  type: string;
  room?: string;
  states: Record<string, StateValue>;
}

// Add other types!

export const listDevices = async (): Promise<Record<string, Device>> => {
  const result = await appliancesApi.get<Record<string, Device>>("/appliances");
  return result.data;
};

export const updateState = async (deviceId: string, state: string, value: StateValue) => {
  const result = await appliancesApi.post(`/appliances/${deviceId}/updateState`, { state: state, value: value })
  return result.data
};

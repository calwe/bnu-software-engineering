import { occupancyApi } from "./client";
import { appliancesApi, } from "./client";
import { type Device } from "@/lib/api/appliances"

export interface OccupancyResponse {
  message: string;
}

export const occupancyCheck = async (): Promise<OccupancyResponse> => {
  const result = await occupancyApi.post<OccupancyResponse>("/occupancy/occupancy_check");
  return result.data;
};

export const getOccupancy = async (): Promise<Record<string, boolean>> => {
  const result = await occupancyApi.get<Record<string, boolean>>("/occupancy");
  return result.data;
};


export const listMonitoringDevices = async (): Promise<Record<string, Device>> => {
  const result = await appliancesApi.get<Record<string, Device>>("/appliances");
  var onlyMonitoring = {}
  for (const [key, value] of Object.entries(result.data)){
    if (value.type == "motion_sensor" || value.type == "camera"){
      onlyMonitoring[key] = value
    }
  }
  return onlyMonitoring;
};
import { occupancyApi } from "./client";


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
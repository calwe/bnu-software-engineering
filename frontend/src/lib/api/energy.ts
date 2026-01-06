import { energyApi } from "./client";

export interface RoomStatus {
  room_id: string;
  room_name: string;
  is_empty: boolean;
}

export interface EnergyResponse {
  message: string;
  room_id: string;
  room_name: string;
  is_empty: boolean;
  lights_turned_on: boolean;
  lights_turned_off: boolean;
  light_names: string[];
}

export interface PowerConsumption {
  total_consumption: number;
  active_devices: number;
  device_breakdown: Record<string, number>;
}

export interface Room {
  name: string;
  is_empty: boolean;
}

export const getRooms = async (): Promise<Record<string, Room>> => {
  const result = await energyApi.get<Record<string, Room>>("/energy/rooms");
  return result.data;
};

export const updateRoomStatus = async (status: RoomStatus): Promise<EnergyResponse> => {
  const result = await energyApi.post<EnergyResponse>("/energy/room-status", status);
  return result.data;
};

export const getPowerConsumption = async (): Promise<PowerConsumption> => {
  const result = await energyApi.get<PowerConsumption>("/energy/consumption");
  return result.data;
};

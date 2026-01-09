import { appliancesApi } from "./client";

export type StateValue = string | number | boolean;

export interface Device {
  name: string;
  type: string;
  room?: string;
  states: Record<string, StateValue>;
}

export interface Light extends Device {
  type: "light";
  states: {
    status: string;
  };
}

export interface Heater extends Device {
  type: "heater";
  states: {
    status: string;
    temperature: number;
  };
}

export interface Door extends Device {
  type: "door";
  states: {
    locked: boolean;
  };
}

export interface FireAlarm extends Device {
  type: "fire_alarm";
  states: {
    status: string;
  };
}

export interface Sprinkler extends Device {
  type: "sprinkler";
  states: {
    status: string;
  };
}

export interface Camera extends Device {
  type: "camera";
  states: {
    status: string;
    peopleDetected: boolean;
  };
}

export interface MotionSensor extends Device {
  type: "motion_sensor";
  states: {
    status: string;
    peopleDetected: boolean;
  };
}


export const listDevices = async (): Promise<Record<string, Device>> => {
  const result = await appliancesApi.get<Record<string, Device>>("/appliances");
  return result.data;
};

export const updateState = async (deviceId: string, state: string, value: StateValue) => {
  const result = await appliancesApi.post(`/appliances/${deviceId}/updateState`, { state: state, value: value })
  return result.data
};

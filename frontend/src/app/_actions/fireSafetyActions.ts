'use server'

import { updateSensorReadings, getSensorReadings } from "@/lib/api/fire_safety"

export async function updateSensors(temperature: number, smokeLevel: number) {
  const response = await updateSensorReadings({
    temperature,
    smoke_level: smokeLevel
  })
  return response
}

export async function getCurrentReadings() {
  const readings = await getSensorReadings()
  return readings
}


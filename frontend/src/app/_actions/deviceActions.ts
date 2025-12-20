'use server'

import { sendCommand } from "@/lib/api/appliances"

export async function toggleLight(id: string, status: string) {
  const newStatus = status === 'on' ? 'off' : 'on'
  await sendCommand(id, { status: newStatus })
  return newStatus
}

export async function toggleFireAlarm(id: string, status: string) {
  const newStatus = status === 'on' ? 'off' : 'on'
  await sendCommand(id, { status: newStatus })
  return newStatus
}

export async function toggleSprinkler(id: string, status: string) {
  const newStatus = status === 'on' ? 'off' : 'on'
  await sendCommand(id, { status: newStatus })
  return newStatus
}

export async function toggleDoorLock(id: string, status: string) {
  const newStatus = status === 'locked' ? 'unlocked' : 'locked'
  await sendCommand(id, { status: newStatus })
  return newStatus
}

'use server'

import { sendCommand } from "@/lib/api/appliances"

export async function toggleLight(id: string, status: string) {
  const newStatus = status === 'on' ? 'off' : 'on'
  await sendCommand(id, { status: newStatus })
  return newStatus
}
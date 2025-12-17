'use server'

import { sendCommand, } from "@/lib/api/security"

export async function toggleSecurityDevice(target: string, index: string, enabled: boolean) {
  const newStatus = !enabled
  await sendCommand(target, index, { enabled: newStatus })
  return newStatus
}

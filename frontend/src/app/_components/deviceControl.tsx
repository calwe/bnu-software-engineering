
"use client"

import { Button } from "@/components/ui/button"
// import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { sendCommand } from "@/lib/api/appliances"
import { useState } from "react"


interface DeviceControlProps {
  id: string
  type: string
  status?: string
  temperature?: number
  locked?: boolean
}

export default function DeviceControl({ id, type, status, temperature, locked }: DeviceControlProps) {
  const [showStatus, setShowStatus] = useState(status)
  
  async function toggleLight(formData: FormData) {
    'use client'
    // const cookieStore = await cookies()
    await sendCommand(id, { status: status === 'on' ? 'off' : 'on' })
    setShowStatus(status === 'on' ? 'off' : 'on')
  }

  if (type === 'light') {
    return (
      <form action={toggleLight}>
        <Button type="submit">{status === 'on' ? 'Turn Off' : 'Turn On'}</Button>
      </form>
    )
  }


  return null
}

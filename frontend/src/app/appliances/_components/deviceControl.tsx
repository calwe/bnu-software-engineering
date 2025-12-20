"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { toggleLight } from "../../_actions/deviceActions"
import { Device } from "@/lib/api/appliances"

interface DeviceControlProps {
  id: string
  device: Device
}

export default function DeviceControl({ id, device }: DeviceControlProps) {
  const { type } = device
  const [showStatus, setShowStatus] = useState(device.status ?? "")

  async function handleClick() {
    try {
      const newStatus = await toggleLight(id, showStatus)
      setShowStatus(newStatus)
    } catch (error) {
      console.log('Error:', error)
    }
  }
  
  if (type === 'light') {
    return (
      <div className="flex flex-col gap-2 items-center">
        <Label>Status: {showStatus}</Label>
        <Button onClick={handleClick}>
          {showStatus === 'on' ? 'Turn Off' : 'Turn On'}
        </Button>
      </div>
    )
  }

  if (type === 'fire_alarm') {
    return (
      <div className="flex flex-col gap-2 items-center">
        <Label>Status: {showStatus}</Label>
        <Button onClick={handleClick}>
          {showStatus === 'on' ? 'Deactivate' : 'Activate'}
        </Button>
      </div>
    )
  } else if (type === 'sprinkler') {
    return (
      <div className="flex flex-col gap-2 items-center">
        <Label>Status: {showStatus}</Label>
        <Button onClick={handleClick}>
          {showStatus === 'on' ? 'Turn Off' : 'Turn On'}
        </Button>
      </div>
    )
  }}
import { useState, useEffect } from "react"
import { Device } from "@/lib/api/appliances"
import { sendCommand } from "@/lib/api/appliances"

interface DeviceControlProps {
  id: string
  device: Device
}

export default function DeviceControl({ id, device }: DeviceControlProps) {
  
  const { type } = device

  const [deviceStatus, setDeviceStatus] = useState(device.status ?? "")

  // Update local state when device prop changes
  useEffect(() => {
    setDeviceStatus(device.status ?? "")
  }, [device.status])

  async function handleClick() {
    try {
      const newStatus = deviceStatus === 'locked' ? 'unlocked' : 'locked'
      await sendCommand(id, { status: newStatus })
      setDeviceStatus(newStatus)
    } catch (error) {
      console.log('Error:', error)
    }
  }

  const StatusLight = () => (
    <span
      className={`inline-block w-8 h-8 rounded-full ${deviceStatus === "on" ? "bg-red-600 animate-pulse" : "bg-gray-300"}`}
      title={deviceStatus === "on" ? "Active" : "Inactive"}
    />
  )
  
  const LockStatus = () => (
    <span
      className={`inline-block w-8 h-8 rounded-full ${deviceStatus === "locked" ? "bg-red-600" : "bg-green-600"}`}
      title={deviceStatus === "locked" ? "Locked" : "Unlocked"}
    />
  )
  
  if (type === 'light') {
    return (
      <div className="flex flex-col gap-2 items-center">
        <div 
          onClick={handleClick} 
          className={`w-14 h-8 flex items-center rounded-full p-1 cursor-pointer
            ${deviceStatus === "on" ? "bg-green-500 justify-end" : "bg-gray-300 justify-start"}
          `}
        >
          <div className="w-6 h-6 bg-white rounded-full shadow-md" />
        </div>
      </div>
    )
  }

  if (type === 'door') {
    return (
      <div className="flex flex-col gap-2 items-center">
          <LockStatus />
      </div>
    )
  }

  if (type === "fire_alarm" || type === "sprinkler") {
    return (
      <div className="flex flex-col gap-2 items-center">
        <StatusLight />
      </div>
    )
  }

  return null
}

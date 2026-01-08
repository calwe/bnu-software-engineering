import { useEffect, useState } from "react"
import { Device } from "@/lib/api/appliances"
import { updateState } from "@/lib/api/appliances"

interface DeviceControlProps {
  id: string
  device: Device
}

export default function DeviceControl({ id, device }: DeviceControlProps) {
  
  const { type } = device

  const [status, setStatus] = useState(device.states.status ?? "")

  async function handleClick() {
    try {
      const newStatus = status === 'on' ? 'off' : 'on'
      await updateState(id, "status", newStatus)
      setStatus(newStatus)
    } catch (error) {
      console.log('Error:', error)
    }
  }

  useEffect(() => setStatus(device.states["status"] ?? ""),
            [device.states["status"]])

  const StatusLight = () => (
    <span
      className={`inline-block w-8 h-8 rounded-full ${status === "on" ? "bg-red-600 animate-pulse" : "bg-gray-300"}`}
      title={status === "on" ? "Active" : "Inactive"}
    />
  )
  
  if (type === 'light') {
    return (
      <div className="flex flex-col gap-2 items-center">
        <div 
          onClick={handleClick} 
          className={`w-14 h-8 flex items-center rounded-full p-1 cursor-pointer
            ${status === "on" ? "bg-green-500 justify-end" : "bg-gray-300 justify-start"}
          `}
        >
          <div className="w-6 h-6 bg-white rounded-full shadow-md" />
        </div>
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

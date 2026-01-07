import { useState } from "react"
import { Device } from "@/lib/api/appliances"
import { sendCommand } from "@/lib/api/appliances"

interface DeviceControlProps {
  id: string
  device: Device
}

export default function DeviceControl({ id, device }: DeviceControlProps) {
  
  const { type } = device
  const status = device.status ?? ""

  const [lightStatus, setLightStatus] = useState(device.status ?? "")
  const [peopleDetected, setPeopleDetected] = useState(device.peopleDetected ?? false)

  async function handleClick() {
    try {
      const newStatus = lightStatus === 'on' ? 'off' : 'on'
      await sendCommand(id, { status: newStatus })
      setLightStatus(newStatus)
    } catch (error) {
      console.log('Error:', error)
    }
  }
  async function handleTest() {
    try {
      const newStatus = !peopleDetected
      await sendCommand(id, { peopleDetected: newStatus })
      setPeopleDetected(newStatus)
    } catch (error) {
      console.log('Error:', error)
    }
  }

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

  if (type === "motion_sensor"){
    return (
      <div className="flex flex-col gap-2 items-center">
        <div 
          onClick={handleTest} 
          className={`w-14 h-8 flex items-center rounded-full p-1 cursor-pointer
            ${peopleDetected ? "bg-green-500 justify-end" : "bg-gray-300 justify-start"}
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

"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { toggleSecurityDevice } from "../../_actions/securityActions"
import { MotionSensor } from "@/lib/api/security"

interface MotionSensorControlProps {
  index: string
  motionSensor: MotionSensor
}

export default function MotionSensorControl({ index, motionSensor }: MotionSensorControlProps) {
  const [getIndex, _] = useState(index)
  const [showStatus, setShowStatus] = useState(motionSensor.enabled)

  async function handleClick() {
    try {
      const newStatus = await toggleSecurityDevice("motionSensors", getIndex, showStatus)
      setShowStatus(newStatus)
    } catch (error) {
      console.log('Error:', error)
    }
  }
  
    return (
        <div className="flex flex-col gap-2 items-center">
        <Label>Status: {showStatus ? "Enabled" : "Disabled"}</Label>
        <Button onClick={handleClick}>
            {showStatus ? "Enable" : "Disable"}
        </Button>
        </div>
    )

}
 
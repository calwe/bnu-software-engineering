"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { Camera } from "@/lib/api/security"
import { toggleSecurityDevice } from "../../_actions/securityActions"

interface CameraControlProps {
  index: string
  camera: Camera
}

export default function CameraControl({ index, camera }: CameraControlProps) {
  const [getIndex, _] = useState(index)
  const [showStatus, setShowStatus] = useState(camera.enabled)

  async function handleClick() {
    try {
      const newStatus = await toggleSecurityDevice("cameras", getIndex, showStatus)
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
 
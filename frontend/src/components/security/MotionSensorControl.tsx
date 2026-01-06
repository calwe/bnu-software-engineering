"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { sendCommand } from "@/lib/api/security"
import React from "react";
import Switch from "react-switch";

interface MotionSensorControlProps {
  access: string
  json: object
  setJSON: any
}

export default function MotionSensorControl({ access, json, setJSON}: MotionSensorControlProps) {
    async function handleChange() {
        try {
            var data = await sendCommand("motionSensors", access, { "enabled":!json["motionSensors"][access].enabled})
            var dataAsString = JSON.stringify(data["message"])
            dataAsString = dataAsString.replace(/^"+|"+$/g, '')
            dataAsString = dataAsString.replace(/\\/g, '')
            setJSON(JSON.parse(dataAsString))
        } catch (error) {
            console.log('Error:', error)
        }
    }
    return (
        <div className="flex flex-col gap-2 items-center">
            <Switch onChange={handleChange} checked={json["motionSensors"][access].enabled}/>
        </div>
    )

}

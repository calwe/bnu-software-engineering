"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { sendCommand } from "@/lib/api/security"
import React, { Component } from "react";
import Switch from "react-switch";

interface CameraControlProps {
  access: string
  json: object
  setJSON: any
}

export default function CameraControl({access, json, setJSON}: CameraControlProps) {
    console.log(typeof(json))
    console.log(typeof(setJSON))
    async function handleChange() {
        try {
            var data = await sendCommand("cameras", access, { "enabled":!json["cameras"][access].enabled})
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
            <Switch onChange={handleChange} checked={json["cameras"][access].enabled}/>
        </div>
    )

}


"use client"

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card";
import CameraControl from "./CameraControl";
import MotionSensorControl from "./MotionSensorControl";
import { useState, useEffect } from "react"
import { getSecurity } from "@/lib/api/security"




export default function SecurityCard() {
  const [securityJSON, setSecurityJSON] = useState({});
  const [loading, setLoading] = useState(true)
  
  
  useEffect(() => {
    async function fetchSecurity() {
      try {
        const data = await getSecurity()
        var dataAsString = JSON.stringify(data["message"])
        dataAsString = dataAsString.replace(/^"+|"+$/g, '')
        dataAsString = dataAsString.replace(/\\/g, '')
        setSecurityJSON(JSON.parse(dataAsString))
        console.log(JSON.parse(dataAsString))
      } catch (error) {
        console.error("Error fetching devices:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchSecurity()
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  var cameraHTML = []
  var i = 0;
  for (let [key, value] of Object.entries(securityJSON["cameras"])) {
    cameraHTML.push(
      <div key={key} className="p-2 grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Camera {i+1}</CardTitle>
              <CardDescription></CardDescription>
              <CardAction>
                <CameraControl access={key} json={securityJSON} setJSON={setSecurityJSON}/>
              </CardAction>
            </CardHeader>
          </Card>
          </div>
    )
    i++
  }

  var motionSensorHTML = []
  i = 0;
  for (let [key, value] of Object.entries(securityJSON["motionSensors"])) {
    motionSensorHTML.push(
      <div key={i} className="p-2 grid gap-6">
          <Card key={JSON.stringify(securityJSON["motionSensors"][key])}>
            <CardHeader>
              <CardTitle>MotionSensor {i+1}</CardTitle>
              <CardDescription> {securityJSON["motionSensors"][key]["enabled"] ? "Motion Detected: " + securityJSON["motionSensors"][key]["motionDetected"].toString() : ""}</CardDescription>
              <CardAction>
                <MotionSensorControl access={key} json={securityJSON}  setJSON={setSecurityJSON}/>
              </CardAction>
            </CardHeader>
          </Card>
          </div>
    )
    i++
  }


  return (
  <Card>
    <CardHeader>
      <CardTitle>Security</CardTitle>
      <CardDescription>Security Systems</CardDescription>
    </CardHeader>
    <CardContent>

      <Card>
        <CardHeader>
          <CardTitle>Cameras</CardTitle>
          <CardDescription></CardDescription>
        </CardHeader>
        <CardContent>
          {cameraHTML}
        </CardContent>
      </Card>
      <br/>
      <Card>
        <CardHeader>
          <CardTitle>Motion Detectors</CardTitle>
          <CardDescription></CardDescription>
        </CardHeader>
        <CardContent>
          {motionSensorHTML}
        </CardContent>
      </Card>
    </CardContent>
  </Card>
  );
}

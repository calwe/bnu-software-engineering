"use client"

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import AutomaticPowerControl from "./AutomaticPowerControl"
import PowerMonitoring from "./PowerMonitoring"

export default function EnergyCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Energy Management</CardTitle>
        <CardDescription>Power Saving and Power Monitoring</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="p-2 grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Automatic Device Control</CardTitle>
              <CardDescription>
                Room lights automatically turn off when it's empty
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AutomaticPowerControl />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Power Monitoring</CardTitle>
              <CardDescription>Monitor power consumption</CardDescription>
            </CardHeader>
            <CardContent>
              <PowerMonitoring />
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  )
}

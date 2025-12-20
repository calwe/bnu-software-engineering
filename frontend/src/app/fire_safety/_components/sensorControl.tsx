"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { updateSensors } from "../../_actions/fireSafetyActions"

export default function SensorControl() {
  const [temperature, setTemperature] = useState("20")
  const [smokeLevel, setSmokeLevel] = useState("0")
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  async function handleUpdate() {
    setLoading(true)
    try {
      const result = await updateSensors(parseFloat(temperature), parseFloat(smokeLevel))
      setResponse(result)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="temperature" className="flex items-center gap-2">
            Temperature (°C)
          </Label>
          <Input
            id="temperature"
            type="number"
            value={temperature}
            onChange={(e) => setTemperature(e.target.value)}
            placeholder="Enter temperature"
          />
          <span className="text-xs text-muted-foreground">Threshold: 60°C
          </span>
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="smoke" className="flex items-center gap-2">
            Smoke Level (0-1)
          </Label>
          <Input
            id="smoke"
            type="number"
            step="0.1"
            min="0"
            max="1"
            value={smokeLevel}
            onChange={(e) => setSmokeLevel(e.target.value)}
            placeholder="Enter smoke level"
          />
          <span className="text-xs text-muted-foreground">Threshold: 0.3</span>
        </div>
      </div>

      <Button onClick={handleUpdate} disabled={loading}>
        {loading ? 'Updating...' : 'Update Sensor Readings'}
      </Button>

        {response.alarm_triggered && <p>Fire Alarm Activated</p>}
        {response.sprinkler_triggered && <p>Sprinklers Activated</p>}
        {!response.alarm_triggered && !response.sprinkler_triggered && (
          <p>All sensor readings normal</p>
        )}
        
    </div>
  )
}
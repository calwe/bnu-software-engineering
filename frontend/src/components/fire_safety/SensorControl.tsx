import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useEffect, useState } from "react"
import { updateSensorReadings } from "@/lib/api/fire_safety"

export default function SensorControl() {
  const [temperature, setTemperature] = useState("20")
  const [smokeLevel, setSmokeLevel] = useState("0")
  const [response, setResponse] = useState<any>(null)

  useEffect(() => {
    const timeout = setTimeout(() => {
      handleUpdate()
    }, 500)

    return () => clearTimeout(timeout)
  }, [temperature, smokeLevel])

  async function handleUpdate() {
    try {
      const result = await updateSensorReadings({
        temperature: parseFloat(temperature),
        smoke_level: parseFloat(smokeLevel)
      })
      setResponse(result)
    } catch (error) {
      console.error('Error:', error)
    } finally {
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
          <span className="text-xs text-muted-foreground">Threshold: 75°C </span>
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
        {response && (
          <p className={response.fire_active ? "text-red-600" : "text-green-600"}>
            {response.fire_active ? "🔥 Fire Alarm Activated" : "✅ All sensor readings normal"}
          </p>
        )}
        
    </div>
  )
}

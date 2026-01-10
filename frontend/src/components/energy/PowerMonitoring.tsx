import { useState, useEffect } from "react"
import { getPowerConsumption } from "@/lib/api/energy"
import type { PowerConsumption } from "@/lib/api/energy"

export default function PowerMonitoring() {
  const [consumption, setConsumption] = useState<PowerConsumption | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadConsumption() {
      try {
        const data = await getPowerConsumption()
        setConsumption(data)
      } catch (error) {
        console.error('Error loading consumption:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadConsumption()
    
    // Information updates every 5 seconds
    const interval = setInterval(loadConsumption, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <div>Loading power data...</div>
  }

  if (!consumption) {
    return <div>No power consumption data available</div>
  }

  return (
    <div className="p-4 border rounded-lg">
      <div className="space-y-2">
        <p className="text-sm">
          <span className="font-medium">Total Consumption:</span> {consumption.total_consumption.toFixed(1)}W
        </p>
        <p className="text-sm">
          <span className="font-medium">Active Devices:</span> {consumption.active_devices}
        </p>
        {Object.keys(consumption.device_breakdown).length > 0 && (
          <div className="mt-2">
            <p className="text-sm font-medium mb-1">Device Breakdown:</p>
            <div className="text-xs space-y-1">
              {Object.entries(consumption.device_breakdown).map(([device, power]) => (
                <div key={device} className="flex justify-between">
                  <span>{device}</span>
                  <span>{power.toFixed(1)}W</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { useState, useEffect } from "react"
import { listDevices, type Device } from "@/lib/api/appliances"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card"
import DeviceControl from "./DeviceControl"

export default function AppliancesCard() {
  const [devices, setDevices] = useState<Record<string, Device>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDevices() {
      try {
        const data = await listDevices()
        setDevices(data)
      } catch (error) {
        console.error("Error fetching devices:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchDevices()

    const interval = setInterval(fetchDevices, 1000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Appliances</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Appliances</CardTitle>
        <CardDescription>Connected Appliances</CardDescription>
      </CardHeader>

      <CardContent>
        {Object.entries(devices).map(([id, device]) => (
          <div key={device.name} className="p-2 grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{device.name}</CardTitle>
                <CardDescription>{device.type}</CardDescription>
                <CardAction>
                  <DeviceControl id={id} device={device} />
                </CardAction>
              </CardHeader>
            </Card>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

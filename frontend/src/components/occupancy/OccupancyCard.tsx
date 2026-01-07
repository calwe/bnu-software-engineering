import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card";
import { useState, useEffect } from "react"
import { occupancyCheck, getOccupancy, listMonitoringDevices } from "@/lib/api/occupancy"
import { type Device } from "@/lib/api/appliances"

export default function OccupancyCard() {
  const [occupancy, setOccupancy] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(true)
  const [monitoringDevices, setMonitoringDevices] = useState<Record<string, Device>>({})

  useEffect(() => {
      handleUpdate();
    }, [JSON.stringify(monitoringDevices)])
  
    async function handleUpdate() {
      try {
        await occupancyCheck()
        console.log("Polled occupancy")
      } catch (error) {
        console.error('Error:', error)
      } finally {
      }
    }

  useEffect(() => {
      async function fetchOccupancy() {
        try {
          const occupancyData = await getOccupancy()
          setOccupancy(occupancyData)
          const monitoringData = await listMonitoringDevices()
          setMonitoringDevices(monitoringData)
        } catch (error) {
          console.error("Error fetching occupancy:", error)
        } finally {
          setLoading(false)
        }
      }
  
      fetchOccupancy()
  
      const interval = setInterval(fetchOccupancy, 1000)
      return () => clearInterval(interval)
    }, [])


  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Occupancy</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    )
  }


  return (
  <Card>
    <CardHeader>
      <CardTitle>Occupancy</CardTitle>
      <CardDescription></CardDescription>
    </CardHeader>
    <CardContent>
      {Object.entries(occupancy).map(([room, occupied]) => (
                <div key={room} className="p-2 grid gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>{room}</CardTitle>
                      <CardDescription>{room} is {occupied ? " " : " not "} occupied.</CardDescription>
                    </CardHeader>
                  </Card>
                </div>
              ))}
    </CardContent>
  </Card>
  );
}

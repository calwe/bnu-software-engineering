import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { getDoors } from "@/lib/api/security"
import { useEffect, useState } from "react"
import Door from "./Door"
import { Device } from "@/lib/api/appliances"

export default function SecurityCard() {
  const [doors, setDoors] = useState<Record<string, Device>>({})
  const [loading, setLoading] = useState(true)

  async function fetchDevices() {
    try {
      const data = await getDoors()
      setDoors(data)
      console.log(doors)
    } catch (error) {
      console.error("Error fetching devices:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDevices()
  }, [])

  if (loading) return (
    <Card>
      <CardHeader>
        <CardTitle>Security System (Loading)</CardTitle>
        <CardDescription>House Access Control</CardDescription>
      </CardHeader>
    </Card>
  )
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Security System</CardTitle>
        <CardDescription>House Access Control</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(doors).map(([id, door]) => (
            <Door 
              key={id} 
              id={id}
              name={door.name}
              locked={door.states["locked"] as boolean} 
              updateDoors={() => fetchDevices()}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

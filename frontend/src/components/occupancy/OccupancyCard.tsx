import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card";
import { useState, useEffect } from "react"
import { occupancyCheck, getOccupancy } from "@/lib/api/occupancy"

export default function SecurityCard() {
  const [occupancy, setOccupancy] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
      const timeout = setInterval(() => {
        handleUpdate()
      }, 2000)
  
      return () => clearInterval(timeout)
    }, [])
  
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
          const data = await getOccupancy()
          setOccupancy(data)
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

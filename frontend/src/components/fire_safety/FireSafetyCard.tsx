import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import SensorControl from "./SensorControl"

export default function FireSafetyCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Fire Safety System</CardTitle>
        <CardDescription>Environmental Sensors</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="p-2 grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Smoke & Temperature Monitoring</CardTitle>
              <CardDescription>Adjust sensor readings to test fire safety responses</CardDescription>
            </CardHeader>
            <CardContent>
              <SensorControl />
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  )
}

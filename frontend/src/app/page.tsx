import { usersService } from "@/lib/api/users";
import { redirect } from "next/navigation";
import { listDevices, sendCommand, type Device } from "@/lib/api/appliances";
import { Card, CardHeader, CardTitle, CardDescription, CardAction, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default async function Home() {
  const session = await usersService.getSession()

  if (!session) {
    redirect('/login')
  }

  const devices = await listDevices()

  return (
    <div className="p-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>Appliances</CardTitle>
          <CardDescription>Connected Appliances</CardDescription>
          {/* <CardAction>
            <Button variant="secondary" size="sm">
              Toggle
            </Button> 
          </CardAction> */}
        </CardHeader>
        <CardContent>
          {devices.map((device : Device) => (
            <div className="p-2 grid gap-6">
              <Card key={device.id}>
                <CardHeader>
                  <CardTitle>{device.id}</CardTitle>
                </CardHeader>
              </Card>
            </div>
          ))}
        </CardContent>
        {/* <CardFooter>
          <p>Last updated: 2 minutes ago</p>
        </CardFooter> */}
      </Card>
    </div>
  )
}

import { usersService } from "@/lib/api/users";
import { redirect } from "next/navigation";
import { listDevices, sendCommand, type Device } from "@/lib/api/appliances";
import { Card, CardHeader, CardTitle, CardDescription, CardAction, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

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
        </CardHeader>
        <CardContent>
          {Object.entries(devices).map(([id, device]: [string, Device]) => (
            <div key={id} className="p-2 grid gap-6">
              <Card key={id}>
                <CardHeader>
                  <CardTitle>{id}</CardTitle>
                  <CardDescription>{device.type}</CardDescription>
                  <CardAction>
                    {device.type === 'light' && (
                      // <Button onClick={() => sendCommand(id, { status: device.status === "on" ? "off" : "on"})}>
                      <Button>
                        Toggle Light
                      </Button>
                    )}
                    {device.type === 'heater' && (
                      <Input>
                      </Input>
                    )}
                    {device.type === 'door' && (
                      <Button>
                        {device.locked ? "Unlock Door" : "Lock Door"}
                      </Button>
                    )}
                  </CardAction>
                </CardHeader>
              </Card>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

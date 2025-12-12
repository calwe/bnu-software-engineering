
import { listDevices, type Device } from "@/lib/api/appliances";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card";
import DeviceControl from "./deviceControl";

export default async function AppliancesCard() {
  const devices: Record<string, Device> = await listDevices();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Appliances</CardTitle>
        <CardDescription>Connected Appliances</CardDescription>
      </CardHeader>
      <CardContent>
        {Object.entries(devices).map(([id, device]) => (
          <div key={id} className="p-2 grid gap-6">
            <Card key={id}>
              <CardHeader>
                <CardTitle>{id}</CardTitle>
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
  );
}


import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card";
import CameraControl from "./cameraControl";
import MotionSensorControl from "./motionSensorControl";
import { type Camera, type MotionSensor, getCameras, getMotionSensors } from "@/lib/api/security"


export default async function SecurityCard() {
    const cameras: Record<string, Camera> = await getCameras();
    const motionSensors: Record<string, MotionSensor> = await getMotionSensors();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Security</CardTitle>
        <CardDescription>TO ADD</CardDescription>
      </CardHeader>
      <CardContent>

        <Card>
            <CardHeader>
                <CardTitle>Cameras</CardTitle>
                <CardDescription></CardDescription>
            </CardHeader>
            <CardContent>
                {Object.entries(cameras).map(([i, camera]) => (
                        <div key={i} className="p-2 grid gap-6">
                        <Card key={i}>
                            <CardHeader>
                            <CardTitle>Camera {i}</CardTitle>
                            <CardDescription></CardDescription>
                            <CardAction>
                                <CameraControl index={i} camera={camera} />
                            </CardAction>
                            </CardHeader>
                        </Card>
                        </div>
                    ))}
            </CardContent>
        </Card>
        <br/>
        <Card>
            <CardHeader>
                <CardTitle>Motion Detectors</CardTitle>
                <CardDescription></CardDescription>
            </CardHeader>
            <CardContent>
                {Object.entries(motionSensors).map(([i, motionSensor]) => (
                          <div key={i} className="p-2 grid gap-6">
                            <Card key={i}>
                              <CardHeader>
                                <CardTitle>Motion Sensor {i}</CardTitle>
                                <CardDescription>Motion detected: {motionSensor.motionDetected ? "True": "False"}</CardDescription>
                                <CardAction>
                                  <MotionSensorControl index={i} motionSensor={motionSensor} />
                                </CardAction>
                              </CardHeader>
                            </Card>
                          </div>
                        ))}
            </CardContent>
            
        </Card>

      </CardContent>
    </Card>
  );
}

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "../ui/button"
import { LockIcon, UnlockIcon } from "lucide-react"
import { lockDoor, unlockDoor } from "@/lib/api/security"

interface DoorProps {
 id: string,
 name: string,
 locked: boolean,
 updateDoors: () => void
}

export default function Door({ id, name, locked, updateDoors }: DoorProps) {
  async function lock() {
    try {
      await lockDoor(id)
      updateDoors()
    } catch (error) {
      console.error("Error locking door:", error)
    }
  }

  async function unlock() {
    try {
      await unlockDoor(id)
      updateDoors()
    } catch (error) {
      console.error("Error unlocking door:", error)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">{name}</CardTitle>
        {locked &&
          <CardDescription className="text-center text-green-400">Locked</CardDescription>
        || 
          <CardDescription className="text-center text-red-400">Unlocked</CardDescription>
        }
      </CardHeader>
      <CardContent>
        <div className="flex gap-6 justify-center">
          <Button variant="secondary" onClick={lock}>
            <LockIcon />
          </Button>
          <Button variant="secondary" onClick={unlock}>
            <UnlockIcon />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { useState, useEffect } from "react"
import { getRooms, updateRoomStatus } from "@/lib/api/energy"
import type { Room } from "@/lib/api/energy"

export default function AutomaticPowerControl() {
  const [rooms, setRooms] = useState<Record<string, Room>>({})
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        const roomsData = await getRooms()
        setRooms(roomsData)
      } catch (error) {
        console.error('Error loading data:', error)
      }
    }
    loadData()
  }, [])

  async function handleRoomToggle(roomId: string) {
    setLoading(true)
    try {
      const room = rooms[roomId]
      const result = await updateRoomStatus({
        room_id: roomId,
        room_name: room.name,
        is_empty: !room.is_empty
      })
      setResponse(result)
      
      setRooms(prev => ({
        ...prev,
        [roomId]: {
          ...prev[roomId],
          is_empty: !prev[roomId].is_empty
        }
      }))
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-4">
        {Object.entries(rooms).map(([roomId, room]) => (
          <div key={roomId} className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <Label className="text-base font-medium">{room.name}</Label>
              <p className="text-sm text-muted-foreground">
                Status: {room.is_empty ? "Empty" : "Occupied"}
              </p>
            </div>
            <Button 
              onClick={() => handleRoomToggle(roomId)} 
              disabled={loading}
              variant={room.is_empty ? "outline" : "default"}
            >
              {room.is_empty ? "Mark Occupied" : "Mark Empty"}
            </Button>
          </div>
        ))}
      </div>

      {response && (
        <div className="p-4 rounded-lg">
          {response.lights_turned_off && response.light_names && response.light_names.length > 0 && (
            <div>
              <p className="font-medium">
                Lights automatically turned off in {response.room_name}:
              </p>
              <ul className="list-disc list-inside ml-2 mt-1">
                {response.light_names.map((lightName: string, index: number) => (
                  <li key={index} className="text-sm">{lightName}</li>
                ))}
              </ul>
            </div>
          )}
          {response.lights_turned_on && response.light_names && response.light_names.length > 0 && (
            <div>
              <p className="font-medium">
                Lights automatically turned on in {response.room_name}:
              </p>
              <ul className="list-disc list-inside ml-2 mt-1">
                {response.light_names.map((lightName: string, index: number) => (
                  <li key={index} className="text-sm">{lightName}</li>
                ))}
              </ul>
            </div>
          )}
          {!response.lights_turned_on && !response.lights_turned_off && response.is_empty && (
            <p>
              No lights found in {response.room_name}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

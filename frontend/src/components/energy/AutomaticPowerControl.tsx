"use client"

import { Label } from "@/components/ui/label"
import { useState, useEffect } from "react"
import { getOccupancy } from "@/lib/api/occupancy"
import { getRooms, autoControl } from "@/lib/api/energy"
import type { Room } from "@/lib/api/energy"

export default function AutomaticPowerControl() {
  const [rooms, setRooms] = useState<Record<string, Room>>({})
  const [occupancy, setOccupancy] = useState<Record<string, boolean>>({})

  useEffect(() => {
    async function loadData() {
      try {
        const roomsData = await getRooms()
        const occupancyData = await getOccupancy()
        setRooms(roomsData)
        setOccupancy(occupancyData)
      } catch (error) {
        console.error('Error loading data:', error)
      }
    }
    
    async function runAutoControl() {
      try {
        const result = await autoControl()
        if (result.changes && result.changes.length > 0) {
          await loadData()
        }
      } catch (error) {
        console.error('Error running auto-control:', error)
      }
    }
    
    loadData()
    runAutoControl()
    
    // Poll occupancy and trigger auto-control every 5 seconds
    const interval = setInterval(() => {
      loadData()
      runAutoControl()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-4">
        {Object.entries(rooms).map(([roomId, room]) => {
          const isOccupied = occupancy[roomId] || false
          return (
            <div key={roomId} className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <Label className="text-base font-medium">{room.name}</Label>
                <p className="text-xs text-muted-foreground mt-1">
                  {isOccupied 
                    ? "Lights On" 
                    : "Lights Off"}
                </p>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                isOccupied 
                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" 
                  : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
              }`}>
                {isOccupied ? "Occupied" : "Empty"}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

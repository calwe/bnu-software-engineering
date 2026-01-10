import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { usersService } from "@/lib/api/users"
import AppliancesCard from "@/components/appliances/AppliancesCard"
import FireSafetyCard from "@/components/fire_safety/FireSafetyCard"
import EnergyCard from "@/components/energy/EnergyCard"
import OccupancyCard from "@/components/occupancy/OccupancyCard"
import SecurityCard from "@/components/security/SecurityCard"

export default function HomePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function checkSession() {
      const session = await usersService.getSession()
      
      if (!session) {
        navigate('/login')
      } else {
        setLoading(false)
      }
    }

    checkSession()
  }, [navigate])

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Smart Home Dashboard</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <AppliancesCard />
        <div className="flex flex-col gap-6">
          <FireSafetyCard />
          <SecurityCard />
          <OccupancyCard />
        </div>
        <EnergyCard />
      </div>
    </div>
  )
}

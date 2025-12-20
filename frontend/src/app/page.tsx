import { usersService } from "@/lib/api/users";
import { redirect } from "next/navigation";
import AppliancesCard from "./appliances/_components/appliancesCard";
import  FireSafetyCard  from "./fire_safety/_components/fireSafetyCard"

export default async function Home() {
  const session = await usersService.getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Smart Home Dashboard</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        
          <AppliancesCard/>
       
        <FireSafetyCard />
      </div>
    </div>
  )
}

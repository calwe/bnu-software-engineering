import { usersService } from "@/lib/api/users";
import { redirect } from "next/navigation";
import AppliancesCard from "./appliances/_components/appliancesCard";

export default async function Home() {
  const session = await usersService.getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="p-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <AppliancesCard/>
    </div>
  )
}

import { usersService } from "@/lib/api/users";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await usersService.getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="flex justify-center items-center min-h-screen">
      <h1 className="text-xl">Welcome {session.sub}</h1>
    </div>
  )
}

import { usersService } from "@/lib/api/users";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await usersService.getSession()

  if (!session) {
    redirect('/login')
  }

  return <h1>Welcome {session.sub}</h1>
}

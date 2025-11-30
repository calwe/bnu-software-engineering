import { cookies } from "next/headers";

export async function getUserName() {
  const cookieStore = await cookies()
}

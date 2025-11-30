import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { usersService } from "@/lib/api/users"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"

export default function LoginCard() {
  async function login(formData: FormData) {
    'use server'

    const cookieStore = await cookies()

    const loginRequest = {
      username: formData.get('username') as string,
      password: formData.get('password') as string,
    }

    try {
      const response = await usersService.login(loginRequest)
      cookieStore.set('jwt', response.token, {
        maxAge: response.expires_in,
        path: '/'
      })
    } catch (error) {
      console.error("Error: ", error)
      throw error
    }

    redirect('/')
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>Login to your account</CardTitle>
        <CardDescription>
          Login to your account to access the dashboard
        </CardDescription>
      </CardHeader>
      <form action={login}>
        <div className="flex flex-col gap-6">
          <CardContent>
            <div className="flex flex-col gap-4">
              <div className="grid gap-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="janedoe1"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" name="password" type="password" required />
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex-col gap-2">
            <Button type="submit" className="w-full">
              Login
            </Button>
          </CardFooter>
        </div>
      </form>
    </Card>
  )
}


import { usersApi } from "./client"

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  expires_in: number
}

export interface Session {
  session_id: string
  sub: string
  iat: number
  exp: number
}

export const usersService = {
  login: async (request: LoginRequest) => {
    const response = await usersApi.post<LoginResponse>('/login', request)

    return response.data
  },

  getSession: async () => {
    try {
      const response = await usersApi.get<Session>('/getSession')
      return response.data
    } catch {
      return null
    }
  }
}

import { usersApi } from "./client"

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  message: string
}

export const usersService = {
  login: async (request: LoginRequest) => {
    const response = await usersApi.post<LoginResponse>('/login', request)

    return response.data
  }
}

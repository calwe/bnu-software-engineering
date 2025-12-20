import axios, { AxiosInstance } from 'axios'
import { cookies } from 'next/headers'

const USERS_SERVICE_URL = process.env.USERS_SERVICE_URL || 'http://localhost:8001'
const APPLIANCES_SERVICE_URL = process.env.APPLIANCES_SERVICE_URL || 'http://localhost:8002'
const FIRE_SAFETY_SERVICE_URL = process.env.FIRE_SAFETY_SERVICE_URL || 'http://localhost:8003'

export const usersApi = createApiClient(USERS_SERVICE_URL)
export const appliancesApi = createApiClient(APPLIANCES_SERVICE_URL)
export const fireSafetyApi = createApiClient(FIRE_SAFETY_SERVICE_URL)

// client helper functions

function createApiClient(baseURL: string): AxiosInstance {
    const client = axios.create({
        baseURL,
        timeout: 10000,
        headers: {
            'Content-Type': 'application/json',
        },
    })

    client.interceptors.request.use(
        async (config) => {
            const token = await getAuthToken()
            
            if (token) {
                config.headers.Authorization = `Bearer ${token}`
            }

            return config
        },
    )

    return client
}

async function getAuthToken() {
  const cookieClient = await cookies()
  return cookieClient.get("jwt")?.value
}

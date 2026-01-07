import axios, { AxiosInstance } from 'axios'

const USERS_SERVICE_URL = import.meta.env.VITE_USERS_SERVICE_URL || 'http://localhost:8001'
const APPLIANCES_SERVICE_URL = import.meta.env.VITE_APPLIANCES_SERVICE_URL || 'http://localhost:8002'
const FIRE_SAFETY_SERVICE_URL = import.meta.env.VITE_FIRE_SAFETY_SERVICE_URL || 'http://localhost:8003'
const ENERGY_SERVICE_URL = import.meta.env.VITE_ENERGY_SERVICE_URL || 'http://localhost:8004'
const SECURITY_SERVICE_URL = import.meta.env.VITE_SECURITY_SERVICE_URL || 'http://localhost:8006'

export const usersApi = createApiClient(USERS_SERVICE_URL)
export const appliancesApi = createApiClient(APPLIANCES_SERVICE_URL)
export const fireSafetyApi = createApiClient(FIRE_SAFETY_SERVICE_URL)
export const energyApi = createApiClient(ENERGY_SERVICE_URL)
export const securityApi = createApiClient(SECURITY_SERVICE_URL)

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
        (config) => {
            const token = getAuthToken()
            
            if (token) {
                config.headers.Authorization = `Bearer ${token}`
            }

            return config
        },
    )

    return client
}

function getAuthToken() {
  return localStorage.getItem("jwt")
}


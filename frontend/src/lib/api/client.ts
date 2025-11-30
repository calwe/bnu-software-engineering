import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const USERS_SERVICE_URL = process.env.USERS_SERVICE_URL || 'http://localhost:8001'

export const usersApi = createApiClient(USERS_SERVICE_URL)

function createApiClient(baseURL: string): AxiosInstance {
    const client = axios.create({
        baseURL,
        timeout: 10000,
        headers: {
            'Content-Type': 'application/json',
        },
    })

    return client
}

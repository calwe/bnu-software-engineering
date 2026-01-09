/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USERS_SERVICE_URL?: string
  readonly VITE_APPLIANCES_SERVICE_URL?: string
  readonly VITE_FIRE_SAFETY_SERVICE_URL?: string
  readonly VITE_ENERGY_SERVICE_URL?: string
  readonly VITE_OCCUPANCY_SERVICE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

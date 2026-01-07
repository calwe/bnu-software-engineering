import { securityApi } from "./client";


export interface SecurityResponse {
  message: string;
}

export const securityCheck = async (): Promise<SecurityResponse> => {
  const result = await securityApi.post<SecurityResponse>("/security_monitoring/security_check");
  return result.data;
};
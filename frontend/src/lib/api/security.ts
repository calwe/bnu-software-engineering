import { securityApi } from "./client";

export const getSecurity = async (): Promise<Record<string, string>> => {
    const result = await securityApi.get<Record<string, string>>("/security");
    return result.data;
};

export const sendCommand = async (target: string, id: string, command: Record<string, any>) => {
    const result = await securityApi.post("/security/" + target + "/" + id + "/command", command)
    return result.data
}

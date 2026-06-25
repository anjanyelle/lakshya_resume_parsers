import axios from "axios";
import type { ApplicationData } from "../features/apply/types/application";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function submitApplication(application: ApplicationData) {
  const response = await axios.post(`${baseURL}/api/v1/applications`, application);
  return response.data;
}

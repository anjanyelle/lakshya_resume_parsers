import axios from "axios";
import type { ApplicationData } from "../types/application";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const applicationClient = axios.create({
  baseURL,
  timeout: 20000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function submitApplication(application: ApplicationData) {
  const response = await applicationClient.post("/api/v1/applications", application);
  return response.data;
}

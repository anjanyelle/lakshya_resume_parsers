import axios, { type AxiosError, type AxiosRequestConfig } from "axios";
import { useAuthStore as useSimpleAuthStore } from "../../store/authStore";

// Backend API (Node.js) - Authentication, Candidates, etc.
const backendURL = import.meta.env.VITE_BACKEND_URL || "http://localhost:3001";

// AI Service API (Python) - Resume parsing
const aiServiceURL = import.meta.env.VITE_AI_SERVICE_URL || "http://localhost:8000";

// Auth client - no interceptors for login/register
export const authClient = axios.create({
  baseURL: backendURL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Main API client - with interceptors for authenticated requests
export const apiClient = axios.create({
  baseURL: backendURL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const aiServiceClient = axios.create({
  baseURL: aiServiceURL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshingPromise: Promise<string> | null = null;

const refreshToken = async () => {
  const {
    accessToken: token,
    clearTokens,
  } = useSimpleAuthStore.getState();
  if (!token) {
    clearTokens();
    throw new Error("Missing access token");
  }
  
  // Note: The current backend doesn't have a refresh endpoint
  // For now, we'll just clear tokens and force re-login
  // In production, you'd implement a proper refresh token mechanism
  clearTokens();
  throw new Error("Token expired. Please login again.");
};

apiClient.interceptors.request.use((config) => {
  const { accessToken } = useSimpleAuthStore.getState();
  if (accessToken) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    } as any;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & {
      _retry?: boolean;
      _retryCount?: number;
    };
    const status = error.response?.status;

    if (status === 401 && !original?._retry) {
      original._retry = true;
      try {
        refreshingPromise = refreshingPromise || refreshToken();
        const newToken = await refreshingPromise;
        refreshingPromise = null;
        original.headers = {
          ...original.headers,
          Authorization: `Bearer ${newToken}`,
        };
        return apiClient(original);
      } catch {
        refreshingPromise = null;
        useSimpleAuthStore.getState().clearTokens();
      }
    }

    const shouldRetry = !status || status >= 500;
    if (shouldRetry && (original?._retryCount ?? 0) < 2) {
      original._retryCount = (original._retryCount ?? 0) + 1;
      await new Promise((resolve) =>
        setTimeout(resolve, 400 * (original._retryCount ?? 1)),
      );
      return apiClient(original);
    }

    const message =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      "Unexpected API error";
    return Promise.reject(new Error(message));
  },
);

export const createAbortController = () => new AbortController();

// Export the base URLs for reference
export { backendURL, aiServiceURL };

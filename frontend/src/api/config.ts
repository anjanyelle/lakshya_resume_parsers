// API Configuration for different environments
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_CONFIG = {
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

// Export individual endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  
  // File operations
  UPLOAD: '/upload',
  PARSE: '/parsing/parse',
  
  // Candidates
  CANDIDATES: '/candidates',
  CANDIDATE: (id: string) => `/candidates/${id}`,
  
  // Jobs
  JOBS: '/jobs',
  JOB: (id: string) => `/jobs/${id}`,
  
  // Health
  HEALTH: '/health',
};

export default API_CONFIG;

import { apiClient } from './client'

export type AuthTokens = {
  access_token: string
  refresh_token: string
  token_type: string
}

export const login = async (email: string, password: string) => {
  const response = await apiClient.post<AuthTokens>('/api/v1/auth/login', {
    email,
    password,
  })
  return response.data
}

export const register = async (
  email: string,
  password: string,
  role: string,
) => {
  const response = await apiClient.post('/api/v1/auth/register', {
    email,
    password,
    role,
  })
  return response.data
}

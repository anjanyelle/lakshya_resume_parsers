import { create } from 'zustand'

type AuthState = {
  accessToken: string | null
  refreshToken: string | null
  user: { email: string; role: string } | null
  setTokens: (accessToken: string, refreshToken: string, user?: { email: string; role: string }) => void
  clearTokens: () => void
}

const ACCESS_KEY = 'resume_parser_access_token'
const REFRESH_KEY = 'resume_parser_refresh_token'

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem(ACCESS_KEY),
  refreshToken: localStorage.getItem(REFRESH_KEY),
  user: JSON.parse(localStorage.getItem('user_data') || 'null'),
  setTokens: (accessToken, refreshToken, user) => {
    localStorage.setItem(ACCESS_KEY, accessToken)
    localStorage.setItem(REFRESH_KEY, refreshToken)
    if (user) localStorage.setItem('user_data', JSON.stringify(user))
    set({ accessToken, refreshToken, user: user || null })
  },
  clearTokens: () => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem('user_data')
    set({ accessToken: null, refreshToken: null, user: null })
  },
}))

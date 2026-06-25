import { create } from "zustand";

interface User {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setTokens: (accessToken: string, refreshToken: string, user?: User) => void;
  clearTokens: () => void;
  setUser: (user: User) => void;
};

const ACCESS_KEY = "resume_parser_access_token";
const REFRESH_KEY = "resume_parser_refresh_token";
const USER_KEY = "resume_parser_user";

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem(ACCESS_KEY),
  refreshToken: localStorage.getItem(REFRESH_KEY),
  user: localStorage.getItem(USER_KEY) ? JSON.parse(localStorage.getItem(USER_KEY)!) : null,
  setTokens: (accessToken, refreshToken, user) => {
    localStorage.setItem(ACCESS_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken || accessToken); // Use same token if refresh not provided
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      set({ user });
    }
    set({ accessToken, refreshToken: refreshToken || accessToken });
  },
  clearTokens: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    set({ accessToken: null, refreshToken: null, user: null });
  },
  setUser: (user) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ user });
  },
}));

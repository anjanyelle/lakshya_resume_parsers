import { create } from "zustand";
import api from "../services/api";

interface UserPermission {
  module_name: string;
  action_name: string;
}

interface Permission {
  id: string;
  module_name: string;
  action_name: string;
  description?: string;
}

interface PermissionState {
  userPermissions: UserPermission[];  // Current user's permissions
  allPermissions: Permission[];        // Full permission catalog
  isLoading: boolean;
  error: string | null;
  fetchUserPermissions: () => Promise<void>;
  fetchAllPermissions: () => Promise<void>;
  hasPermission: (module: string, action: string) => boolean;
  clearError: () => void;
  reset: () => void;
}

export const usePermissionStore = create<PermissionState>((set, get) => ({
  userPermissions: [],
  allPermissions: [],
  isLoading: false,
  error: null,

  fetchUserPermissions: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get("/api/permissions/me");
      set({ 
        userPermissions: response.data.permissions || [], 
        isLoading: false 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || "Failed to fetch user permissions";
      set({ error: errorMessage, isLoading: false });
    }
  },

  fetchAllPermissions: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get("/api/permissions");
      set({ 
        allPermissions: response.data.permissions || [], 
        isLoading: false 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || "Failed to fetch permission catalog";
      set({ error: errorMessage, isLoading: false });
    }
  },

  hasPermission: (module: string, action: string) => {
    const { userPermissions } = get();
    return userPermissions.some(
      permission => 
        permission.module_name === module && 
        permission.action_name === action
    );
  },

  clearError: () => set({ error: null }),

  reset: () => set({ 
    userPermissions: [], 
    allPermissions: [], 
    isLoading: false, 
    error: null 
  }),
}));

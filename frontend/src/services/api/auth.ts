import { authClient } from "./client";

export type AuthTokens = {
  token: string;
  refresh_token?: string;
  token_type?: string;
  user?: {
    id: string;
    email: string;
    role: string;
    created_at: string;
  };
};

export type AuthResponse = {
  message: string;
  user: {
    id: string;
    email: string;
    role: string;
    created_at: string;
  };
  token: string;
};

export const login = async (email: string, password: string): Promise<AuthTokens> => {
  const response = await authClient.post<AuthResponse>("/api/auth/login", {
    email,
    password,
  });
  
  return {
    token: response.data.token,
    refresh_token: response.data.token, // Backend uses same token for both
    token_type: "Bearer",
    user: response.data.user,
  };
};

export const register = async (
  email: string,
  password: string,
  role: string,
): Promise<AuthTokens> => {
  const response = await authClient.post<AuthResponse>("/api/auth/register", {
    email,
    password,
    role,
  });
  
  return {
    token: response.data.token,
    refresh_token: response.data.token, // Backend uses same token for both
    token_type: "Bearer",
    user: response.data.user,
  };
};

/**
 * Smart authentication that handles login and auto-registration
 * 1. Tries to login first
 * 2. If login fails with 401, attempts registration with "jobapply" role
 * 3. If registration succeeds, auto-login
 * 4. Returns auth tokens and user info
 */
export const authenticateOrRegister = async (
  email: string,
  password: string
): Promise<{ tokens: AuthTokens; isNewUser: boolean }> => {
  try {
    // First, try to login
    const tokens = await login(email, password);
    return { tokens, isNewUser: false };
  } catch (loginError: any) {
    // Check if it's a 401 error (invalid credentials)
    const errorMessage = loginError.message || "";
    const isInvalidCredentials = errorMessage.includes("Invalid email or password") || 
                                errorMessage.includes("Invalid credentials") ||
                                loginError.response?.status === 401;
    
    if (isInvalidCredentials) {
      try {
        // Attempt registration with "jobapply" role
        await register(email, password, "jobapply");
        
        // Auto-login after successful registration
        const loginTokens = await login(email, password);
        
        return { tokens: loginTokens, isNewUser: true };
      } catch (registerError: any) {
        // If registration fails with 409, user exists but password is wrong
        const registerErrorMessage = registerError.message || "";
        if (registerErrorMessage.includes("already exists") || registerError.response?.status === 409) {
          throw new Error("Invalid password. User already exists with this email.");
        }
        // Other registration errors
        throw new Error(registerErrorMessage || "Registration failed. Please try again.");
      }
    }
    // Other login errors
    throw loginError;
  }
};

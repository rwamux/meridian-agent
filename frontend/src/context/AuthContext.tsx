import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { authApi, setAuthToken } from "../api/client";

interface User {
  name: string;
  customer_id: string;
  email: string;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (email: string, pin: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const SESSION_KEY = "meridian_session";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = sessionStorage.getItem(SESSION_KEY);
    return stored ? JSON.parse(stored).user : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    const stored = sessionStorage.getItem(SESSION_KEY);
    return stored ? JSON.parse(stored).token : null;
  });

  useEffect(() => {
    if (token) setAuthToken(token);
  }, [token]);

  const login = useCallback(async (email: string, pin: string) => {
    const { data } = await authApi.login(email, pin);
    const newUser = {
      name: data.customer_name,
      customer_id: data.customer_id,
      email,
    };
    setUser(newUser);
    setToken(data.access_token);
    setAuthToken(data.access_token);
    sessionStorage.setItem(
      SESSION_KEY,
      JSON.stringify({ user: newUser, token: data.access_token })
    );
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    setAuthToken(null);
    sessionStorage.removeItem(SESSION_KEY);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, login, logout, isAuthenticated: !!token }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

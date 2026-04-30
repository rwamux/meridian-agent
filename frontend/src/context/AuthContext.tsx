import { ReactNode, createContext, useCallback, useContext, useEffect, useState } from "react";
import { authApi, setAuthToken } from "../api/client";

interface User {
  name: string;
  customer_id: string;
  email: string;
}

interface AuthContextValue {
  user: User | null;
  login: (email: string, pin: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const SESSION_KEY = "meridian_session";

function loadSession(): { user: User; token: string } | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => loadSession()?.user ?? null);

  useEffect(() => {
    const session = loadSession();
    if (session) setAuthToken(session.token);
  }, []);

  const login = useCallback(async (email: string, pin: string) => {
    const { data } = await authApi.login(email, pin);
    const newUser = { name: data.customer_name, customer_id: data.customer_id, email };
    setUser(newUser);
    setAuthToken(data.access_token);
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({ user: newUser, token: data.access_token }));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setAuthToken(null);
    sessionStorage.removeItem(SESSION_KEY);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

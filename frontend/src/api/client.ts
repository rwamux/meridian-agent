import axios from "axios";

export const api = axios.create({ baseURL: "/api" });

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  customer_name: string;
  customer_id: string;
}

export interface ChatResponse {
  response: string;
  history: ChatMessage[];
}

export const authApi = {
  login: (email: string, pin: string) =>
    api.post<LoginResponse>("/auth/login", { email, pin }),
};

export const chatApi = {
  send: (message: string, history: ChatMessage[]) =>
    api.post<ChatResponse>("/chat", { message, history }),
};

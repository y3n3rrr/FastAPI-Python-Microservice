import { apiFetch } from "@/services/http";
import type { LoginResponse, RegisterPayload } from "@/features/auth/types";

export function login(email: string, password: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/login", {
    method: "POST",
    body: { email, password },
  });
}

export function register(payload: RegisterPayload): Promise<unknown> {
  return apiFetch("/register", {
    method: "POST",
    body: payload,
  });
}

"use client";

import { useMemo } from "react";
import { decodeJwtSub, getAuthToken } from "@/lib/auth";

export function useAuthUserId(): number | null {
  return useMemo(() => {
    const token = getAuthToken();
    if (!token) return null;
    return decodeJwtSub(token);
  }, []);
}

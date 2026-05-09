"use client";

import { useEffect, useState } from "react";
import { decodeJwtSub, getAuthToken } from "@/lib/auth";

export function UserBadge() {
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;
    setUserId(decodeJwtSub(token));
  }, []);

  if (!userId) return null;

  return <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Signed in as user #{userId}</p>;
}

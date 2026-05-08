"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken } from "@/lib/auth";
import type { Transaction } from "@/features/orders/types";
import { listTransactions } from "@/features/orders/services/orders-service";

export function useTransactions() {
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const token = getAuthToken();
      if (!token) {
        router.push("/login");
        return;
      }
      try {
        const data = await listTransactions(token);
        setTransactions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load transactions");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [router]);

  return { transactions, loading, error };
}

"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/features/auth/services/auth-service";
import { setAuthToken } from "@/lib/auth";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("checkout-tester@example.com");
  const [password, setPassword] = useState("supersecure");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login(email, password);
      setAuthToken(data.access_token);
      router.push("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-7 shadow-card">
      <h1 className="text-3xl font-black">Welcome back</h1>
      <p className="mt-2 text-sm text-slate-600">Log in to browse products and place orders.</p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <input className="w-full rounded-xl border border-slate-300 px-4 py-3" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="w-full rounded-xl border border-slate-300 px-4 py-3" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <Button type="submit" disabled={loading} className="w-full">{loading ? "Signing in..." : "Sign In"}</Button>
      </form>
      <p className="mt-5 text-sm text-slate-600">No account? <Link href="/register" className="font-semibold text-coral">Create one</Link></p>
    </div>
  );
}

"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "@/features/auth/services/auth-service";
import { Button } from "@/components/ui/Button";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("Shop");
  const [surname, setSurname] = useState("User");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("supersecure");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ name, surname, email, password, is_active: true });
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg rounded-3xl border border-slate-200 bg-white p-7 shadow-card">
      <h1 className="text-3xl font-black">Create account</h1>
      <form onSubmit={onSubmit} className="mt-6 grid gap-4 sm:grid-cols-2">
        <input className="rounded-xl border border-slate-300 px-4 py-3" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
        <input className="rounded-xl border border-slate-300 px-4 py-3" value={surname} onChange={(e) => setSurname(e.target.value)} placeholder="Surname" />
        <input className="sm:col-span-2 rounded-xl border border-slate-300 px-4 py-3" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" type="email" />
        <input className="sm:col-span-2 rounded-xl border border-slate-300 px-4 py-3" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
        {error ? <p className="sm:col-span-2 text-sm text-red-600">{error}</p> : null}
        <Button type="submit" disabled={loading} className="sm:col-span-2">{loading ? "Creating..." : "Create Account"}</Button>
      </form>
    </div>
  );
}

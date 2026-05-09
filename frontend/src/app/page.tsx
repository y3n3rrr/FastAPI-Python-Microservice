import Link from "next/link";
import { ROUTES } from "@/constants/routes";

export default function HomePage() {
  return (
    <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="fade-rise rounded-3xl border border-slate-200/70 bg-white/90 p-8 shadow-card">
        <p className="mb-3 inline-flex rounded-full bg-coral/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-coral">New Season Deals</p>
        <h1 className="text-4xl font-black leading-tight text-ink md:text-5xl">Shop smarter, checkout faster, track every order.</h1>
        <p className="mt-4 max-w-xl text-slate-600">MigroShop connects your FastAPI commerce backend to a clean storefront with secure auth, one-tap checkout, and live transaction visibility.</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href={ROUTES.products} className="rounded-xl bg-ink px-5 py-3 font-semibold text-white hover:opacity-95">Start Shopping</Link>
          <Link href={ROUTES.transactions} className="rounded-xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 hover:bg-slate-100">View Transactions</Link>
        </div>
      </div>
      <div className="fade-rise rounded-3xl bg-gradient-to-br from-jade to-emerald-500 p-8 text-white shadow-card">
        <h2 className="text-2xl font-extrabold">Why this frontend?</h2>
        <ul className="mt-5 space-y-3 text-sm text-emerald-50">
          <li>React 19 + Next.js App Router</li>
          <li>Tailwind-driven shopping UI</li>
          <li>FastAPI JWT authentication integration</li>
          <li>Checkout + PaymentIntent + Transactions flow</li>
        </ul>
      </div>
    </section>
  );
}

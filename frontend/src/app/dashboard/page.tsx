import Link from "next/link";
import { ROUTES } from "@/constants/routes";

export default function DashboardPage() {
  return (
    <section className="space-y-4">
      <h1 className="text-3xl font-black">Dashboard</h1>
      <p className="text-slate-600">Quick operational overview for your storefront flows.</p>
      <div className="grid gap-4 sm:grid-cols-3">
        <Link href={ROUTES.products} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">Products</Link>
        <Link href={ROUTES.checkout} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">Checkout</Link>
        <Link href={ROUTES.transactions} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">Transactions</Link>
      </div>
    </section>
  );
}

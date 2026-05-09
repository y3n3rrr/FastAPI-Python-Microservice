import Link from "next/link";
import { ROUTES } from "@/constants/routes";

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 xl:block">
      <div className="sticky top-24 space-y-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
        <h3 className="text-sm font-bold uppercase tracking-[0.14em] text-slate-500">Quick Access</h3>
        <Link href={ROUTES.products} className="block rounded-lg px-3 py-2 text-sm font-semibold text-ink hover:bg-slate-100">Browse products</Link>
        <Link href={ROUTES.checkout} className="block rounded-lg px-3 py-2 text-sm font-semibold text-ink hover:bg-slate-100">Go to checkout</Link>
        <Link href={ROUTES.transactions} className="block rounded-lg px-3 py-2 text-sm font-semibold text-ink hover:bg-slate-100">View transactions</Link>
        <Link href={ROUTES.assistant} className="block rounded-lg px-3 py-2 text-sm font-semibold text-ink hover:bg-slate-100">Open assistant</Link>
      </div>
    </aside>
  );
}

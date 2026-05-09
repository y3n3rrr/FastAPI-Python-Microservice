"use client";

import type { Transaction } from "@/features/orders/types";

export function TransactionList({ transactions }: { transactions: Transaction[] }) {
  if (!transactions.length) {
    return <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-slate-600">No transactions yet.</div>;
  }

  return (
    <div className="space-y-4">
      {transactions.map((tx) => (
        <article key={tx.payment_intent.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h3 className="text-lg font-extrabold text-ink">PaymentIntent #{tx.payment_intent.id}</h3>
            <span className="rounded-full bg-jade/10 px-3 py-1 text-xs font-bold uppercase tracking-wide text-jade">{tx.payment_intent.status}</span>
          </div>
          <p className="mt-2 text-sm text-slate-500">{tx.payment_intent.amount} {tx.payment_intent.currency} via {tx.payment_intent.provider}</p>
          <div className="mt-4 grid gap-2 text-sm text-slate-700 sm:grid-cols-3">
            <p><span className="font-semibold">Order:</span> {tx.order?.id ?? "-"}</p>
            <p><span className="font-semibold">Order status:</span> {tx.order?.status ?? "-"}</p>
            <p><span className="font-semibold">Lines:</span> {tx.order_items.length}</p>
          </div>
        </article>
      ))}
    </div>
  );
}

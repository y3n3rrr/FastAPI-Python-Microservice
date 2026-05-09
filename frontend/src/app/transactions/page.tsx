"use client";

import { TransactionList } from "@/features/orders/components/TransactionList";
import { useTransactions } from "@/features/orders/hooks/useTransactions";

export default function TransactionsPage() {
  const { transactions, loading, error } = useTransactions();

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-4xl font-black">My Transactions</h1>
        <p className="text-slate-600">Payment intents and linked checkout orders.</p>
      </div>
      {loading ? <p className="text-slate-600">Loading transactions...</p> : null}
      {error ? <p className="text-red-600">{error}</p> : null}
      {!loading && !error ? <TransactionList transactions={transactions} /> : null}
    </section>
  );
}

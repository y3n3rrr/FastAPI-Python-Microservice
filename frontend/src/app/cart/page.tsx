"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken } from "@/lib/auth";
import type { CheckoutLocalItem } from "@/features/orders/types";

const STORE_KEY = "checkout_items";

export default function CartPage() {
  const router = useRouter();
  const [items, setItems] = useState<CheckoutLocalItem[]>([]);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push("/login");
      return;
    }
    const raw = localStorage.getItem(STORE_KEY);
    setItems(raw ? JSON.parse(raw) : []);
  }, [router]);

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-4xl font-black">Cart</h1>
        <p className="text-slate-600">Review what you selected from products.</p>
      </div>

      {!items.length ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-slate-600">Cart is empty. Add products first.</div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.product_variant_id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
              <p className="font-bold text-ink">{item.title}</p>
              <p className="text-sm text-slate-500">Variant #{item.product_variant_id}</p>
              <p className="mt-2 text-sm font-semibold">Quantity: {item.quantity}</p>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        <Link href="/products" className="rounded-xl border border-slate-300 px-4 py-2 font-semibold text-slate-700 hover:bg-slate-100">Back to Products</Link>
        <Link href="/checkout" className="rounded-xl bg-ink px-4 py-2 font-semibold text-white hover:opacity-90">Go to Checkout</Link>
      </div>
    </section>
  );
}

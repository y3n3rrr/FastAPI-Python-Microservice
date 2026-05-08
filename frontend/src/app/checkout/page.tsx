"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { decodeJwtSub, getAuthToken } from "@/lib/auth";
import { CheckoutCart } from "@/features/orders/components/CheckoutCart";
import { placeCheckout } from "@/features/orders/services/orders-service";
import type { CheckoutLocalItem, CheckoutResponse } from "@/features/orders/types";

const STORE_KEY = "checkout_items";

export default function CheckoutPage() {
  const router = useRouter();
  const [items, setItems] = useState<CheckoutLocalItem[]>([]);
  const [note, setNote] = useState("Quick order from Next.js storefront");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<CheckoutResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push("/login");
      return;
    }
    const raw = localStorage.getItem(STORE_KEY);
    setItems(raw ? JSON.parse(raw) : []);
  }, [router]);

  const hasItems = useMemo(() => items.length > 0, [items]);

  function removeItem(variantId: number) {
    const next = items.filter((x) => x.product_variant_id !== variantId);
    setItems(next);
    localStorage.setItem(STORE_KEY, JSON.stringify(next));
  }

  async function submitCheckout() {
    setStatus("");
    setResult(null);

    const token = getAuthToken();
    if (!token) {
      router.push("/login");
      return;
    }

    const userId = decodeJwtSub(token);
    if (!userId) {
      setStatus("Could not resolve user id from token. Please login again.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = await placeCheckout(token, userId, items, note);
      setResult(payload);
      setStatus("Checkout successful.");
      localStorage.removeItem(STORE_KEY);
      setItems([]);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Checkout failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="space-y-6">
      <div className="fade-rise">
        <h1 className="text-4xl font-black">Checkout</h1>
        <p className="text-slate-600">Review selections and create order + payment intent.</p>
      </div>

      <CheckoutCart items={items} onRemove={removeItem} />

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
        <label className="text-sm font-semibold text-slate-700">Order note</label>
        <textarea value={note} onChange={(e) => setNote(e.target.value)} className="mt-2 h-24 w-full rounded-xl border border-slate-300 px-3 py-2" />
        <button type="button" onClick={submitCheckout} disabled={!hasItems || isSubmitting} className="mt-4 rounded-xl bg-ink px-5 py-3 font-semibold text-white disabled:opacity-60">
          {isSubmitting ? "Placing order..." : "Place order"}
        </button>
      </div>

      {status ? <p className="font-semibold text-slate-700">{status}</p> : null}

      {result ? (
        <div className="rounded-2xl border border-jade/30 bg-jade/5 p-5">
          <h2 className="text-2xl font-extrabold text-jade">Order Confirmed</h2>
          <p className="mt-2 text-sm">Order #{result.order.id} | PaymentIntent #{result.payment_intent.id}</p>
          <p className="text-sm">Total: {result.order.total_amount} {result.order.currency}</p>
        </div>
      ) : null}
    </section>
  );
}

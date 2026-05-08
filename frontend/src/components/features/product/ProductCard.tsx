"use client";

import { useState } from "react";
import type { ProductVariant } from "@/features/orders/types";
import { Button } from "@/components/ui/Button";

type Props = {
  variant: ProductVariant;
  productName: string;
};

export function ProductCard({ variant, productName }: Props) {
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);

  function addToCart() {
    const prev = localStorage.getItem("checkout_items");
    const items: Array<{ product_variant_id: number; quantity: number; title: string }> = prev ? JSON.parse(prev) : [];
    const found = items.find((x) => x.product_variant_id === variant.id);
    if (found) found.quantity += qty;
    else items.push({ product_variant_id: variant.id, quantity: qty, title: productName });
    localStorage.setItem("checkout_items", JSON.stringify(items));
    setAdded(true);
    setTimeout(() => setAdded(false), 1200);
  }

  return (
    <article className="fade-rise rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-jade">{variant.sku}</p>
      <h2 className="mt-2 text-xl font-bold">{productName}</h2>
      <p className="mt-2 text-sm text-slate-500">{variant.name}</p>
      <p className="mt-5 text-2xl font-extrabold text-ink">{variant.price} {variant.currency}</p>
      <div className="mt-4 flex items-center gap-2">
        <input type="number" min={1} value={qty} onChange={(e) => setQty(Number(e.target.value || 1))} className="w-20 rounded-lg border border-slate-300 px-2 py-1" />
        <Button onClick={addToCart}>Add</Button>
        {added ? <span className="text-xs font-semibold text-jade">Added</span> : null}
      </div>
    </article>
  );
}

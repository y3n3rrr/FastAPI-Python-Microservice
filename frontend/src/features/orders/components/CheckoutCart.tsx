"use client";

import { useMemo } from "react";
import type { CheckoutLocalItem } from "@/features/orders/types";

type Props = {
  items: CheckoutLocalItem[];
  onRemove: (variantId: number) => void;
};

export function CheckoutCart({ items, onRemove }: Props) {
  const totalQty = useMemo(() => items.reduce((acc, item) => acc + item.quantity, 0), [items]);

  if (!items.length) {
    return <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-slate-600">Your checkout cart is empty. Add products from catalog.</div>;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm font-semibold text-slate-600">{totalQty} item(s) ready</p>
      {items.map((item) => (
        <div key={item.product_variant_id} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
          <div>
            <p className="font-bold text-ink">{item.title}</p>
            <p className="text-sm text-slate-500">Variant #{item.product_variant_id}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold">x{item.quantity}</span>
            <button type="button" onClick={() => onRemove(item.product_variant_id)} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 hover:bg-slate-100">Remove</button>
          </div>
        </div>
      ))}
    </div>
  );
}

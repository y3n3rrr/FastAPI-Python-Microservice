import { apiFetch, API_BASE } from "@/lib/api-client";
import type { CheckoutLocalItem, CheckoutResponse, Product, ProductVariant, Transaction } from "@/features/orders/types";

export function listProducts(token: string): Promise<Product[]> {
  return apiFetch<Product[]>("/catalog/products", { token });
}

export function listVariants(token: string): Promise<ProductVariant[]> {
  return apiFetch<ProductVariant[]>("/catalog/variants", { token });
}

export function listTransactions(token: string): Promise<Transaction[]> {
  return apiFetch<Transaction[]>("/checkout/transactions", { token });
}

export async function placeCheckout(token: string, userId: number, items: CheckoutLocalItem[], note: string): Promise<CheckoutResponse> {
  const idempotencyKey = crypto.randomUUID();
  const response = await fetch(`${API_BASE}/checkout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify({
      user_id: userId,
      items: items.map(({ product_variant_id, quantity }) => ({ product_variant_id, quantity })),
      note,
    }),
  });

  const body = (await response.json()) as CheckoutResponse | { detail?: string };
  if (!response.ok) {
    throw new Error((body as { detail?: string }).detail ?? "Checkout failed");
  }

  return body as CheckoutResponse;
}

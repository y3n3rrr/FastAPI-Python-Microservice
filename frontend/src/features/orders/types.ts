export type Product = {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  is_active: boolean;
};

export type ProductVariant = {
  id: number;
  product_id: number;
  sku: string;
  name: string;
  price: string;
  currency: string;
  is_active: boolean;
};

export type CheckoutResponse = {
  payment_intent: {
    id: number;
    amount: string;
    currency: string;
    status: string;
    provider: string;
    created_at?: string;
  };
  order: {
    id: number;
    status: string;
    total_amount: string;
    currency: string;
    created_at?: string;
  };
  order_items: Array<{
    id: number;
    product_variant_id: number;
    quantity: number;
    line_total: string;
    currency: string;
  }>;
};

export type Transaction = {
  payment_intent: CheckoutResponse["payment_intent"];
  order: CheckoutResponse["order"] | null;
  order_items: CheckoutResponse["order_items"];
};

export type CheckoutLocalItem = {
  product_variant_id: number;
  quantity: number;
  title: string;
};

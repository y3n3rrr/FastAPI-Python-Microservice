import type { Product, ProductVariant } from "@/features/orders/types";
import { ProductCard } from "@/components/features/product/ProductCard";

type Props = {
  products: Product[];
  variants: ProductVariant[];
};

export function ProductList({ products, variants }: Props) {
  const cards = variants
    .filter((variant) => variant.is_active)
    .map((variant) => ({
      variant,
      product: products.find((p) => p.id === variant.product_id),
    }))
    .filter((row) => row.product?.is_active);

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {cards.map((item) => (
        <ProductCard key={item.variant.id} variant={item.variant} productName={item.product?.name ?? "Item"} />
      ))}
    </div>
  );
}

import { notFound, redirect } from "next/navigation";
import { cookies } from "next/headers";
import { listProducts, listVariants } from "@/features/orders/services/orders-service";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const token = (await cookies()).get("auth_token")?.value;
  if (!token) redirect("/login");

  const resolved = await params;
  const productId = Number(resolved.id);

  const [products, variants] = await Promise.all([listProducts(token), listVariants(token)]);
  const product = products.find((p) => p.id === productId);
  if (!product) notFound();

  const productVariants = variants.filter((v) => v.product_id === productId);

  return (
    <section className="space-y-4">
      <h1 className="text-4xl font-black">{product.name}</h1>
      <p className="text-slate-600">{product.description ?? "No product description available."}</p>
      <div className="grid gap-3 md:grid-cols-2">
        {productVariants.map((variant) => (
          <div key={variant.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-jade">{variant.sku}</p>
            <p className="mt-1 font-bold">{variant.name}</p>
            <p className="mt-2 text-lg font-extrabold">{variant.price} {variant.currency}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

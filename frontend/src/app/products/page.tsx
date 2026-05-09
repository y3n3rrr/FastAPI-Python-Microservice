import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { ProductList } from "@/components/features/product/ProductList";
import { listProducts, listVariants } from "@/features/orders/services/orders-service";

export default async function ProductsPage() {
  const token = (await cookies()).get("auth_token")?.value;
  if (!token) redirect("/login");

  const [products, variants] = await Promise.all([listProducts(token), listVariants(token)]);

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-4xl font-black">Products</h1>
        <p className="text-slate-600">Pick variants and add them to cart.</p>
      </div>
      <ProductList products={products} variants={variants} />
    </section>
  );
}

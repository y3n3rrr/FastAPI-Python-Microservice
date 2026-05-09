import Link from "next/link";

export default function NotFound() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
      <h1 className="text-2xl font-black">Page not found</h1>
      <p className="mt-2 text-slate-600">This route does not exist in MigroShop.</p>
      <Link href="/" className="mt-4 inline-block rounded-lg bg-ink px-4 py-2 font-semibold text-white">Go home</Link>
    </div>
  );
}

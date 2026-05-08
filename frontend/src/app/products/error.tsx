"use client";

export default function ProductsError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
      <h2 className="text-lg font-bold text-red-700">Products failed to load</h2>
      <p className="text-sm text-red-600">{error.message}</p>
      <button type="button" onClick={reset} className="mt-3 rounded-lg bg-red-600 px-3 py-2 text-sm font-semibold text-white">Retry</button>
    </div>
  );
}

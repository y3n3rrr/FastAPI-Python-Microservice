"use client";

export default function DashboardError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
      <h2 className="text-lg font-bold text-red-700">Dashboard failed</h2>
      <p className="text-sm text-red-600">{error.message}</p>
      <button onClick={reset} type="button" className="mt-3 rounded-lg bg-red-600 px-3 py-2 text-sm font-semibold text-white">Retry</button>
    </div>
  );
}

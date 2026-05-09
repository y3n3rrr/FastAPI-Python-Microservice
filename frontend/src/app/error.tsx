"use client";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
      <h2 className="text-xl font-bold text-red-700">Something went wrong</h2>
      <p className="mt-2 text-sm text-red-600">{error.message}</p>
      <button type="button" onClick={reset} className="mt-3 rounded-lg bg-red-600 px-3 py-2 text-sm font-semibold text-white">Try again</button>
    </div>
  );
}

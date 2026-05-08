"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";

type Props = {
  disabled?: boolean;
  onSend: (message: string) => Promise<void>;
};

export function ChatComposer({ disabled, onSend }: Props) {
  const [message, setMessage] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || disabled) return;
    setMessage("");
    await onSend(text);
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <label className="text-sm font-semibold text-slate-700">Ask assistant</label>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        rows={4}
        placeholder="Type your question..."
        className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2"
      />
      <div className="mt-3 flex justify-end">
        <Button type="submit" disabled={disabled || !message.trim()}>
          Send
        </Button>
      </div>
    </form>
  );
}

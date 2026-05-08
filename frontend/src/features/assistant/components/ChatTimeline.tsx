"use client";

import type { AssistantMessage } from "@/features/assistant/types";

type Props = {
  messages: AssistantMessage[];
  loading?: boolean;
};

export function ChatTimeline({ messages, loading }: Props) {
  if (!messages.length) {
    return <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-slate-600">No messages yet. Start a conversation.</div>;
  }

  return (
    <div className="space-y-3">
      {messages.map((message) => {
        const isUser = message.role === "user";
        return (
          <article
            key={message.id}
            className={`rounded-2xl p-4 shadow-card ${
              isUser ? "ml-8 border border-coral/30 bg-coral/5" : "mr-8 border border-jade/30 bg-jade/5"
            }`}
          >
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">{message.role}</p>
            <p className="mt-1 whitespace-pre-wrap text-sm text-slate-800">{message.content}</p>
          </article>
        );
      })}
      {loading ? <p className="text-sm text-slate-500">Assistant is thinking...</p> : null}
    </div>
  );
}

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken } from "@/lib/auth";
import { ChatComposer } from "@/features/assistant/components/ChatComposer";
import { ChatTimeline } from "@/features/assistant/components/ChatTimeline";
import { useAssistantChat } from "@/features/assistant/hooks/useAssistantChat";
import { Button } from "@/components/ui/Button";

export default function AssistantPage() {
  const router = useRouter();
  const { messages, sessionId, loading, error, sendMessage, resetSession } = useAssistantChat();

  useEffect(() => {
    if (!getAuthToken()) {
      router.push("/login");
    }
  }, [router]);

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-4xl font-black">Assistant Chat</h1>
          <p className="text-slate-600">Connected to backend `/assistant/chat` endpoints.</p>
          <p className="mt-1 text-xs text-slate-500">Session: {sessionId ?? "new"}</p>
        </div>
        <Button variant="secondary" onClick={resetSession}>New Session</Button>
      </div>

      {error ? <p className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

      <ChatTimeline messages={messages} loading={loading} />
      <ChatComposer disabled={loading} onSend={sendMessage} />
    </section>
  );
}

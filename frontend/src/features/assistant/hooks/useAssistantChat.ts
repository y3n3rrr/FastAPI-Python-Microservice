"use client";

import { useCallback, useEffect, useState } from "react";
import { decodeJwtSub, getAuthToken } from "@/lib/auth";
import type { AssistantMessage } from "@/features/assistant/types";
import { listAssistantMessages, sendAssistantMessage } from "@/features/assistant/services/assistant-service";

const SESSION_KEY = "assistant_session_id";

export function useAssistantChat() {
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async (token: string, targetSessionId: number) => {
    const history = await listAssistantMessages(token, targetSessionId);
    setMessages(history);
  }, []);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;

    const persisted = localStorage.getItem(SESSION_KEY);
    const parsed = persisted ? Number(persisted) : null;
    if (parsed && Number.isFinite(parsed)) {
      setSessionId(parsed);
      void fetchHistory(token, parsed).catch(() => {
        localStorage.removeItem(SESSION_KEY);
        setSessionId(null);
        setMessages([]);
      });
    }
  }, [fetchHistory]);

  const sendMessage = useCallback(
    async (text: string) => {
      setError("");
      const token = getAuthToken();
      if (!token) {
        setError("Please login first.");
        return;
      }

      const userId = decodeJwtSub(token);
      if (!userId) {
        setError("Invalid login token. Please login again.");
        return;
      }

      setLoading(true);
      try {
        const response = await sendAssistantMessage(token, {
          user_id: userId,
          message: text,
          ...(sessionId ? { session_id: sessionId } : {}),
        });

        const nextSessionId = response.session.id;
        setSessionId(nextSessionId);
        localStorage.setItem(SESSION_KEY, String(nextSessionId));

        setMessages((prev) => {
          const existing = new Set(prev.map((item) => item.id));
          const candidates = [response.user_message, response.assistant_message];
          const toAppend = candidates.filter((item) => !existing.has(item.id));
          return [...prev, ...toAppend];
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
      } finally {
        setLoading(false);
      }
    },
    [sessionId],
  );

  const resetSession = useCallback(() => {
    localStorage.removeItem(SESSION_KEY);
    setSessionId(null);
    setMessages([]);
    setError("");
  }, []);

  return {
    messages,
    sessionId,
    loading,
    error,
    sendMessage,
    resetSession,
  };
}

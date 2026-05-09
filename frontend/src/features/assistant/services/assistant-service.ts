import { apiFetch } from "@/services/http";
import type { AssistantChatResponse, AssistantMessage } from "@/features/assistant/types";

export function sendAssistantMessage(
  token: string,
  payload: { user_id: number; message: string; session_id?: number },
): Promise<AssistantChatResponse> {
  return apiFetch<AssistantChatResponse>("/assistant/chat", {
    method: "POST",
    token,
    body: payload,
  });
}

export function listAssistantMessages(token: string, sessionId: number): Promise<AssistantMessage[]> {
  return apiFetch<AssistantMessage[]>(`/assistant/chat/sessions/${sessionId}/messages`, {
    token,
  });
}

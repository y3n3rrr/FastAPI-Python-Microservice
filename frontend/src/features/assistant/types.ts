export type AssistantRole = "user" | "assistant";

export type AssistantMessage = {
  id: number;
  session_id: number;
  role: AssistantRole;
  content: string;
  model: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type AssistantSession = {
  id: number;
  user_id: number;
  title: string | null;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
};

export type AssistantChatResponse = {
  session: AssistantSession;
  user_message: AssistantMessage;
  assistant_message: AssistantMessage;
};

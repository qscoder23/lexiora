/** API 客户端及 SSE 解析 */

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  domain?: string;
  domain_zh?: string;
  sources?: string[];
}

export interface StepEvent {
  step: "intent" | "retrieve" | "generate";
  status: "completed" | "pending";
  domain?: string;
  domain_zh?: string;
  intent?: string;
  sources_count?: number;
  answer?: string;
}

export interface DoneEvent {
  sources: string[];
}

export interface ErrorEvent {
  message: string;
}

export type SSEEvent =
  | { type: "step"; data: StepEvent }
  | { type: "done"; data: DoneEvent }
  | { type: "error"; data: ErrorEvent };

export async function* parseSSEStream(
  response: Response
): AsyncGenerator<SSEEvent, void, unknown> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";
  let currentEventType = "step";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEventType = line.slice(6).trim();
        continue;
      }
      if (line.startsWith("data:")) {
        const dataStr = line.slice(5).trim();
        try {
          const data = JSON.parse(dataStr);
          yield { type: currentEventType, data } as SSEEvent;
        } catch {
          // ignore parse errors
        }
      }
    }
  }
}

export async function sendChat(
  question: string,
  history: { question: string; answer: string }[]
): Promise<Response> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
  return response;
}

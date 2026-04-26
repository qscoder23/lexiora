import { ChatMessage } from "@/lib/api";
import { UserMessage } from "./UserMessage";
import { AssistantMessage } from "./AssistantMessage";

interface MessageListProps {
  messages: ChatMessage[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="flex flex-col gap-4">
      {messages.map((msg, idx) => {
        if (msg.role === "user") {
          return <UserMessage key={idx} content={msg.content} />;
        }
        return (
          <AssistantMessage
            key={idx}
            content={msg.content}
            domain={msg.domain}
            domain_zh={msg.domain_zh}
            sources={msg.sources}
          />
        );
      })}
    </div>
  );
}

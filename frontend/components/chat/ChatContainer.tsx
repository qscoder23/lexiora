"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { ChatMessage, SSEEvent, sendChat, parseSSEStream } from "@/lib/api";
import { MessageList } from "./MessageList";
import { AssistantMessage } from "./AssistantMessage";
import { InputArea } from "./InputArea";
import { StatusBar } from "./StatusBar";
import { Header } from "@/components/layout/Header";

export function ChatContainer() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingAnswer, setStreamingAnswer] = useState("");
  const [pendingDomain, setPendingDomain] = useState("");
  const [pendingDomainZh, setPendingDomainZh] = useState("");
  const [pendingSources, setPendingSources] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingAnswer]);

  const handleSend = useCallback(async (question: string) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setIsLoading(true);
    setCurrentStep("intent");
    setStreamingAnswer("");

    let lastAnswer = "";
    let domain = "";
    let domainZh = "";
    let collectedSources: string[] = [];

    try {
      const response = await sendChat(question, []);
      const eventStream = parseSSEStream(response);

      for await (const event of eventStream) {
        if (event.type === "step") {
          const step = event.data;
          setCurrentStep(step.step);

          if (step.step === "intent") {
            domain = step.domain ?? "general";
            domainZh = step.domain_zh ?? "通用";
            setPendingDomain(domain);
            setPendingDomainZh(domainZh);
          }

          if (step.step === "generate" && step.answer) {
            lastAnswer = step.answer;
            setStreamingAnswer(step.answer);
          }
        } else if (event.type === "done") {
          collectedSources = event.data.sources;
          setPendingSources(collectedSources);
        } else if (event.type === "error") {
          lastAnswer = `错误: ${event.data.message}`;
          setStreamingAnswer(lastAnswer);
        }
      }

      if (lastAnswer) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: lastAnswer,
            domain,
            domain_zh: domainZh,
            sources: collectedSources,
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "请求失败，请检查后端服务是否运行。" },
      ]);
    } finally {
      setIsLoading(false);
      setCurrentStep(null);
      setStreamingAnswer("");
    }
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 sm:py-6">
        <div className="max-w-2xl mx-auto space-y-6">
          <StatusBar currentStep={currentStep} />
          {messages.length === 0 && !isLoading && (
            <div className="text-center py-16 space-y-3">
              <div className="text-4xl">⚖️</div>
              <h2 className="text-xl font-medium text-text-primary">Lexiora 法律咨询助手</h2>
              <p className="text-sm text-text-secondary">
                多Agent协作 · GraphRAG检索 · 专业知识问答
              </p>
            </div>
          )}
          <MessageList messages={messages} />
          {streamingAnswer && (
            <div className="relative">
              <AssistantMessage
                content={streamingAnswer}
                domain={pendingDomain}
                domain_zh={pendingDomainZh}
                sources={pendingSources}
              />
              <span className="absolute bottom-3 left-4 text-accent-gold cursor-blink">▋</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="border-t border-border px-4 sm:px-6 py-3 sm:py-4">
        <div className="max-w-2xl mx-auto">
          <InputArea onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}

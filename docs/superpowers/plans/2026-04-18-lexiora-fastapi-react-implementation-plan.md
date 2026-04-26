# Lexiora FastAPI + Next.js 重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Streamlit UI 替换为 FastAPI + Next.js App Router，实现 SSE 流式对话和深色极简 UI。

**Architecture:** FastAPI 作为 HTTP 包装层调用现有 `src/` 核心模块（不做改动），Next.js App Router 实现深色极简风格对话界面。Monorepo 结构，`backend/` 与 `frontend/` 并列。

**Tech Stack:** FastAPI + uvicorn + sse-starlette (后端) | Next.js 15 + TypeScript + Tailwind CSS (前端)

---

## 文件结构

```
lexiora/
├── backend/
│   ├── main.py                    # FastAPI 入口、CORS、中间件
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py               # POST /api/chat SSE 端点
│   │   └── health.py             # GET /api/health
│   ├── services/
│   │   ├── __init__.py
│   │   └── streamer.py           # SSE 事件发送器
│   ├── config.py                 # 复用 src/config.py
│   └── requirements.txt
├── frontend/                      # Next.js App Router
│   ├── app/
│   │   ├── layout.tsx            # 根布局
│   │   ├── page.tsx              # 对话页 /
│   │   └── about/
│   │       └── page.tsx          # 关于页 /about
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── UserMessage.tsx
│   │   │   ├── AssistantMessage.tsx
│   │   │   ├── InputArea.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── ui/
│   │   │   └── Badge.tsx
│   │   └── layout/
│   │       └── Header.tsx
│   ├── lib/
│   │   └── api.ts                # API 客户端 + SSE 解析
│   ├── styles/
│   │   └── globals.css           # Tailwind + CSS 变量
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── package.json
```

---

## 任务分解

### Task 1: Backend 项目骨架

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/health.py`
- Create: `backend/services/__init__.py`

- [ ] **Step 1: Create backend requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sse-starlette==2.1.0
python-multipart==0.0.9
```

- [ ] **Step 2: Create backend/main.py**

```python
"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, health

app = FastAPI(title="Lexiora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 3: Create backend/routers/__init__.py**

```python
```

- [ ] **Step 4: Create backend/routers/health.py**

```python
"""健康检查"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 5: Create backend/services/__init__.py**

```python
```

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/main.py backend/routers/__init__.py backend/routers/health.py backend/services/__init__.py
git commit -m "feat: add backend project skeleton"
```

---

### Task 2: Backend SSE 流式聊天端点

**Files:**
- Create: `backend/config.py`
- Create: `backend/routers/chat.py`
- Create: `backend/services/streamer.py`

- [ ] **Step 1: Create backend/config.py**

```python
"""复用 src/config.py，路径指向项目根目录"""
from pathlib import Path
import sys

# 将项目根目录加入 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config

__all__ = ["load_config"]
```

- [ ] **Step 2: Create backend/services/streamer.py**

```python
"""SSE 事件发送器"""
import asyncio
import json
from typing import AsyncGenerator

async def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def step_event(step: str, status: str, **kwargs) -> str:
    return await sse_event("step", {"step": step, "status": status, **kwargs})

async def error_event(message: str) -> str:
    return await sse_event("error", {"message": message})

async def done_event(sources: list[str]) -> str:
    return await sse_event("done", {"sources": sources})
```

- [ ] **Step 3: Create backend/routers/chat.py**

```python
"""POST /api/chat SSE 流式端点"""
import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from backend.services.streamer import step_event, error_event, done_event

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    question = body.get("question", "")
    history = body.get("history", [])

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            # 步骤1: 意图识别
            from src.agents.coordinator import identify_domain
            domain_result = identify_domain(question)
            yield await step_event(
                "intent", "completed",
                domain=domain_result.get("domain", "general"),
                domain_zh=domain_result.get("domain_zh", "通用"),
                intent=domain_result.get("intent", "")
            )

            # 步骤2: 检索（同步调用）
            from src.retrieval.fusion import hybrid_search
            docs = hybrid_search(question)
            sources_count = len(docs)
            yield await step_event("retrieve", "completed", sources_count=sources_count)

            # 步骤3: 生成（同步调用）
            from src.agents.domain_agent import DomainAgent
            agent = DomainAgent(domain_result.get("domain", "general"))
            result = agent.answer(question, domain_result.get("intent", ""), domain_result.get("keywords", []))

            yield await step_event("generate", "completed", answer=result.get("answer", ""))

            # 完成
            yield await done_event(result.get("sources", []))

        except Exception as e:
            yield await error_event(str(e))

    return EventSourceResponse(event_stream())
```

- [ ] **Step 4: 测试健康检查**

Run: `cd backend && python -c "from main import app; print('OK')"`
Expected: 输出 OK，无导入错误

- [ ] **Step 5: Commit**

```bash
git add backend/config.py backend/routers/chat.py backend/services/streamer.py
git commit -m "feat: add SSE chat endpoint with step events"
```

---

### Task 3: Frontend 项目骨架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/next.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`
- Create: `frontend/styles/globals.css`

- [ ] **Step 1: Create frontend/package.json**

```json
{
  "name": "lexiora-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "15.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.6.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/postcss": "^4.0.0"
  }
}
```

- [ ] **Step 2: Create frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 3: Create frontend/tailwind.config.ts**

```ts
import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0D0D0D",
          secondary: "#1A1A1A",
          card: "#21262D",
          hover: "#292E36",
        },
        accent: {
          gold: "#C9A962",
          "gold-dim": "#A68B4B",
          blue: "#4A9EFF",
          red: "#F07178",
          green: "#56D364",
          purple: "#A371F7",
          orange: "#FFA657",
          cyan: "#39C5CF",
        },
        border: "#30363D",
        text: {
          primary: "#E6EDF3",
          secondary: "#8B949E",
          muted: "#6E7681",
        },
      },
      fontFamily: {
        sans: ["Noto Sans SC", "Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
```

- [ ] **Step 4: Create frontend/next.config.ts**

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
```

- [ ] **Step 5: Create frontend/postcss.config.js**

```js
module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

- [ ] **Step 6: Create frontend/styles/globals.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg-primary: #0d0d0d;
  --bg-secondary: #1a1a1a;
  --bg-card: #21262d;
  --bg-hover: #292e36;
  --accent-gold: #c9a962;
  --accent-gold-dim: #a68b4b;
  --accent-blue: #4a9eff;
  --accent-red: #f07178;
  --accent-green: #56d364;
  --accent-purple: #a371f7;
  --accent-orange: #ffa657;
  --accent-cyan: #39c5cf;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --border: #30363d;
}

* {
  box-sizing: border-box;
}

html,
body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: "Noto Sans SC", Inter, system-ui, sans-serif;
}

::-webkit-scrollbar {
  width: 5px;
}
::-webkit-scrollbar-track {
  background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
```

- [ ] **Step 7: Create frontend/app/layout.tsx**

```tsx
import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Lexiora 法律咨询助手",
  description: "多Agent协作 · GraphRAG检索 · 专业知识问答",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 8: Create frontend/app/page.tsx (临时占位)**

```tsx
export default function HomePage() {
  return (
    <main className="min-h-screen bg-bg-primary flex items-center justify-center">
      <h1 className="text-text-primary text-2xl">Lexiora</h1>
    </main>
  );
}
```

- [ ] **Step 9: 验证前端项目可运行**

Run: `cd frontend && npm install && npm run build`
Expected: Build 成功，无报错

- [ ] **Step 10: Commit**

```bash
git add frontend/package.json frontend/tsconfig.json frontend/tailwind.config.ts frontend/next.config.ts frontend/postcss.config.js frontend/styles/globals.css frontend/app/layout.tsx frontend/app/page.tsx
git commit -m "feat: add Next.js project skeleton with Tailwind"
```

---

### Task 4: API 客户端 + SSE 解析

**Files:**
- Create: `frontend/lib/api.ts`

- [ ] **Step 1: Create frontend/lib/api.ts**

```ts
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

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        const eventType = line.slice(6).trim();
        continue;
      }
      if (line.startsWith("data:")) {
        const dataStr = line.slice(5).trim();
        try {
          const data = JSON.parse(dataStr);
          yield { type: "step", data } as SSEEvent;
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/lib/api.ts
git commit -m "feat: add API client with SSE parser"
```

---

### Task 5: Chat UI 核心组件

**Files:**
- Create: `frontend/components/chat/StatusBar.tsx`
- Create: `frontend/components/chat/UserMessage.tsx`
- Create: `frontend/components/chat/AssistantMessage.tsx`
- Create: `frontend/components/chat/MessageList.tsx`
- Create: `frontend/components/chat/InputArea.tsx`
- Create: `frontend/components/chat/ChatContainer.tsx`
- Create: `frontend/components/ui/Badge.tsx`
- Create: `frontend/components/layout/Header.tsx`
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Create frontend/components/ui/Badge.tsx**

```tsx
import clsx from "clsx";

const DOMAIN_STYLES: Record<string, string> = {
  civil_law: "bg-accent-purple/15 text-accent-purple border-accent-purple/30",
  criminal_law: "bg-accent-red/15 text-accent-red border-accent-red/30",
  labor_law: "bg-accent-orange/15 text-accent-orange border-accent-orange/30",
  admin_law: "bg-accent-cyan/15 text-accent-cyan border-accent-cyan/30",
  general: "bg-text-secondary/15 text-text-secondary border-text-secondary/30",
};

const DOMAIN_ICONS: Record<string, string> = {
  civil_law: "⚖️",
  criminal_law: "🔨",
  labor_law: "📋",
  admin_law: "🏛️",
  general: "💬",
};

interface BadgeProps {
  domain: string;
  domain_zh: string;
}

export function DomainBadge({ domain, domain_zh }: BadgeProps) {
  const style = DOMAIN_STYLES[domain] ?? DOMAIN_STYLES.general;
  const icon = DOMAIN_ICONS[domain] ?? DOMAIN_ICONS.general;

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border",
        style
      )}
    >
      {icon} {domain_zh}
    </span>
  );
}
```

- [ ] **Step 2: Create frontend/components/layout/Header.tsx**

```tsx
import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-border bg-bg-secondary px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-xl">⚖️</span>
        <span className="font-semibold text-text-primary">Lexiora</span>
        <span className="text-text-muted text-sm ml-2">法律咨询助手</span>
      </div>
      <nav className="flex items-center gap-4">
        <Link
          href="/"
          className="text-text-secondary hover:text-text-primary text-sm transition-colors"
        >
          对话
        </Link>
        <Link
          href="/about"
          className="text-text-secondary hover:text-text-primary text-sm transition-colors"
        >
          关于
        </Link>
      </nav>
    </header>
  );
}
```

- [ ] **Step 3: Create frontend/components/chat/StatusBar.tsx**

```tsx
import clsx from "clsx";

const STEPS = [
  { key: "intent", label: "识别意图", icon: "🔍" },
  { key: "retrieve", label: "检索知识", icon: "📚" },
  { key: "generate", label: "生成回答", icon: "✍️" },
];

interface StatusBarProps {
  currentStep: string | null;
}

export function StatusBar({ currentStep }: StatusBarProps) {
  const stepIndex = STEPS.findIndex((s) => s.key === currentStep);

  return (
    <div className="flex items-center gap-2 py-2">
      {STEPS.map((step, idx) => {
        const isDone = stepIndex > idx;
        const isActive = stepIndex === idx;

        return (
          <div key={step.key} className="flex items-center gap-2">
            <div
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all",
                isDone && "bg-accent-gold/15 text-accent-gold border-accent-gold/30",
                isActive && "bg-accent-gold/10 text-accent-gold border-accent-gold/20 animate-pulse",
                !isDone && !isActive && "bg-bg-card text-text-muted border-border"
              )}
            >
              <span>{step.icon}</span>
              <span>{step.label}</span>
            </div>
            {idx < STEPS.length - 1 && (
              <div className="w-4 h-px bg-border" />
            )}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 4: Create frontend/components/chat/UserMessage.tsx**

```tsx
interface UserMessageProps {
  content: string;
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <div className="bg-accent-blue text-white px-4 py-3 rounded-2xl rounded-br-md max-w-xl text-sm leading-relaxed">
        {content}
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Create frontend/components/chat/AssistantMessage.tsx**

```tsx
import { useState } from "react";
import { DomainBadge } from "@/components/ui/Badge";

interface AssistantMessageProps {
  content: string;
  domain?: string;
  domain_zh?: string;
  sources?: string[];
}

export function AssistantMessage({
  content,
  domain,
  domain_zh,
  sources = [],
}: AssistantMessageProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2">
      {domain && domain_zh && (
        <DomainBadge domain={domain} domain_zh={domain_zh} />
      )}
      <div className="bg-bg-card border border-border px-4 py-3 rounded-2xl rounded-bl-md max-w-xl text-sm leading-relaxed text-text-primary">
        {content}
      </div>
      {sources.length > 0 && (
        <div>
          <button
            onClick={() => setSourcesOpen(!sourcesOpen)}
            className="text-xs text-text-muted hover:text-accent-gold transition-colors"
          >
            📖 引用来源 ({sources.length})
          </button>
          {sourcesOpen && (
            <ul className="mt-2 space-y-1">
              {sources.map((src, i) => (
                <li
                  key={i}
                  className="text-xs text-text-secondary bg-bg-secondary px-3 py-1.5 rounded-lg border border-border"
                >
                  {src}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Create frontend/components/chat/MessageList.tsx**

```tsx
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
```

- [ ] **Step 7: Create frontend/components/chat/InputArea.tsx**

```tsx
import { useState } from "react";

interface InputAreaProps {
  onSend: (question: string) => void;
  disabled?: boolean;
}

export function InputArea({ onSend, disabled }: InputAreaProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        placeholder="输入法律问题..."
        className="flex-1 bg-bg-card border border-border rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-gold transition-colors disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="bg-accent-gold text-bg-primary px-5 py-3 rounded-xl font-medium text-sm hover:bg-accent-gold-dim transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        发送
      </button>
    </form>
  );
}
```

- [ ] **Step 8: Create frontend/components/chat/ChatContainer.tsx**

```tsx
"use client";

import { useState, useCallback } from "react";
import { ChatMessage, SSEEvent, sendChat, parseSSEStream } from "@/lib/api";
import { MessageList } from "./MessageList";
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

  const handleSend = useCallback(async (question: string) => {
    // 添加用户消息
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setIsLoading(true);
    setCurrentStep("intent");
    setStreamingAnswer("");
    setPendingSources([]);

    try {
      const response = await sendChat(question, []);
      const eventStream = parseSSEStream(response);

      let lastAnswer = "";

      for await (const event of eventStream) {
        if (event.type === "step") {
          const step = event.data;
          setCurrentStep(step.step);

          if (step.step === "intent") {
            setPendingDomain(step.domain ?? "general");
            setPendingDomainZh(step.domain_zh ?? "通用");
          }

          if (step.step === "generate" && step.answer) {
            lastAnswer = step.answer;
            setStreamingAnswer(step.answer);
          }
        } else if (event.type === "done") {
          setPendingSources(event.data.sources);
        } else if (event.type === "error") {
          lastAnswer = `错误: ${event.data.message}`;
          setStreamingAnswer(lastAnswer);
        }
      }

      // 添加助手消息
      if (lastAnswer) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: lastAnswer,
            domain: pendingDomain,
            domain_zh: pendingDomainZh,
            sources: pendingSources,
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
  }, [pendingDomain, pendingDomainZh, pendingSources]);

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex-1 overflow-y-auto px-6 py-6">
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
            <AssistantMessage
              content={streamingAnswer}
              domain={pendingDomain}
              domain_zh={pendingDomainZh}
              sources={pendingSources}
            />
          )}
        </div>
      </div>
      <div className="border-t border-border px-6 py-4">
        <div className="max-w-2xl mx-auto">
          <InputArea onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 9: Update frontend/app/page.tsx**

```tsx
import { ChatContainer } from "@/components/chat/ChatContainer";

export default function HomePage() {
  return <ChatContainer />;
}
```

- [ ] **Step 10: 验证编译**

Run: `cd frontend && npm run build`
Expected: Build 成功

- [ ] **Step 11: Commit**

```bash
git add frontend/components/ frontend/app/page.tsx
git commit -m "feat: add chat UI components with SSE streaming"
```

---

### Task 6: About 页面

**Files:**
- Create: `frontend/app/about/page.tsx`

- [ ] **Step 1: Create frontend/app/about/page.tsx**

```tsx
import { Header } from "@/components/layout/Header";

export default function AboutPage() {
  return (
    <div className="flex flex-col min-h-screen bg-bg-primary">
      <Header />
      <main className="flex-1 px-6 py-12">
        <div className="max-w-2xl mx-auto space-y-8">
          <div className="text-center space-y-3">
            <div className="text-5xl">⚖️</div>
            <h1 className="text-3xl font-bold text-text-primary">Lexiora</h1>
            <p className="text-text-secondary">
              Chinese Legal Consultation Assistant
            </p>
          </div>

          <div className="space-y-6 text-sm text-text-secondary leading-relaxed">
            <section className="space-y-2">
              <h2 className="text-lg font-semibold text-text-primary">项目简介</h2>
              <p>
                Lexiora 是一个基于 Multi-Agent 编排和 GraphRAG 的中文法律咨询助手，支持民法、刑法、劳动法、行政法等多个法律领域的知识问答。
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold text-text-primary">技术架构</h2>
              <ul className="list-disc list-inside space-y-1">
                <li>LLM: Qwen (DashScope)</li>
                <li>Embedding: text-embedding-v3</li>
                <li>Agent: LangGraph StateGraph</li>
                <li>Graph DB: Neo4j Community</li>
                <li>Vector Store: FAISS</li>
                <li>Frontend: Next.js App Router</li>
                <li>Backend: FastAPI + SSE</li>
              </ul>
            </section>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold text-text-primary">核心特性</h2>
              <ul className="list-disc list-inside space-y-1">
                <li>多Agent协作：协调Agent + 领域Agent + 审核Agent</li>
                <li>GraphRAG：向量检索 + 知识图谱双路融合</li>
                <li>流式响应：SSE实时展示推理步骤</li>
                <li>可解释性：答案附带法条引用和来源</li>
              </ul>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/app/about/page.tsx
git commit -m "feat: add about page"
```

---

### Task 7: 前后端联调

- [ ] **Step 1: 启动后端**

Run: `cd backend && python -m uvicorn main:app --reload --port 8000`
Expected: FastAPI 运行在 localhost:8000

- [ ] **Step 2: 测试 /health 端点**

Run: `curl http://localhost:8000/health`
Expected: `{"status":"ok"}`

- [ ] **Step 3: 配置 Next.js 代理（开发环境）**

在 `frontend/next.config.ts` 添加：

```ts
const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};
```

- [ ] **Step 4: 启动前端**

Run: `cd frontend && npm run dev`
Expected: Next.js 运行在 localhost:3000

- [ ] **Step 5: 手动测试完整对话流程**

在浏览器打开 http://localhost:3000，输入问题，验证：
1. Status Bar 步骤正确显示
2. 回答流式渲染
3. 来源正确显示

- [ ] **Step 6: Commit**

```bash
git add frontend/next.config.ts
git commit -m "chore: add API proxy rewrite for dev"
```

---

### Task 8: 视觉美化（可选，如时间允许）

- [ ] 动效增强：消息淡入 + 微位移动画
- [ ] 深色主题微调：确保对比度、间距舒适
- [   ] 移动端适配：单栏布局、触摸友好
- [ ] 加载状态：流式输出时的光标闪烁效果

---

## Spec 覆盖检查

| Spec 章节 | 覆盖任务 |
|-----------|---------|
| 整体架构 / Monorepo | Task 1, 3 |
| API 设计 / SSE 事件流 | Task 2 |
| 前端组件 | Task 4, 5 |
| 视觉风格 | Task 8 |
| 关于页 | Task 6 |
| 前后端联调 | Task 7 |

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-04-18-lexiora-fastapi-react-implementation-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?

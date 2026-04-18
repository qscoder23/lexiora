# Lexiora 重构设计：FastAPI + Next.js

**日期**: 2026-04-18
**状态**: 已批准
**目标**: 将 Streamlit UI 替换为 FastAPI (后端) + Next.js App Router (前端)

---

## 1. 整体架构

### 技术栈

- **前端**: Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **后端**: FastAPI (Python) + SSE 流式响应
- **核心逻辑**: 现有 `src/` 模块（coordinator、domain_agent、fusion、rag 等）不做改动
- **部署**: 本地运行 (`localhost:3000` 前端 + `localhost:8000` 后端)

### Monorepo 结构

```
lexiora/
├── backend/               # FastAPI 应用
│   ├── main.py            # 入口、CORS、中间件
│   ├── routers/
│   │   ├── chat.py        # POST /api/chat (SSE)
│   │   └── health.py      # GET /api/health
│   ├── services/
│   │   └── streamer.py    # SSE 事件发送器
│   ├── config.py          # 复用 src/config.py
│   └── requirements.txt
├── frontend/              # Next.js App Router
│   ├── app/
│   │   ├── page.tsx       # 对话页 /
│   │   └── about/page.tsx # 关于页 /about
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── UserMessage.tsx
│   │   │   ├── AssistantMessage.tsx
│   │   │   ├── InputArea.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── ui/            # 通用 UI 组件
│   │   └── layout/
│   │       └── Header.tsx
│   └── lib/
│       └── api.ts         # API 客户端
├── src/                   # 共享核心（现有代码，不改动）
├── config/                # 配置文件
└── tests/
```

### 系统边界

```
Next.js (3000)
    ↓ HTTP/SSE
FastAPI (8000)
    ↓ 直接调用
src/ 核心模块（不改动）
```

---

## 2. API 设计

### REST 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/chat` | 启动对话，返回 SSE 流 |
| `GET` | `/api/health` | 健康检查 |

### SSE 事件流（POST /api/chat）

**请求体**:
```json
{
  "question": "用户问题",
  "history": [
    {"question": "上一轮问题", "answer": "上一轮回答"}
  ]
}
```

**响应事件流**:

```
event: step
data: {"step": "intent", "status": "completed", "domain": "civil_law", "domain_zh": "民法", "intent": "法条查询"}

event: step
data: {"step": "retrieve", "status": "completed", "sources_count": 8}

event: step
data: {"step": "generate", "status": "completed", "answer": "完整的法律回答..."}

event: done
data: {"sources": ["民法 第115条", "民法 第203条"]}
```

### 错误处理

| 情况 | 响应 |
|------|------|
| Neo4j 不可用 | `event: error` → `{"message": "知识库暂时不可用"}` |
| LLM 调用失败 | `event: error` → `{"message": "生成失败，请重试"}` |
| 无检索结果 | 正常返回，`sources` 为空数组 |

---

## 3. 前端设计

### 页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 对话页 | `/` | 主聊天界面 |
| 关于页 | `/about` | 项目介绍、技术架构 |

### 组件树

```
<ChatPage>
├── <Header>                    # Logo + 标题 + 关于链接
├── <ChatContainer>
│   ├── <MessageList>           # 消息流（可滚动）
│   │   ├── <UserMessage>       # 用户问题（右侧气泡）
│   │   └── <AssistantMessage>  # AI 回答（左侧卡片）
│   │       ├── <DomainBadge>   # 领域标签（彩色小徽章）
│   │       ├── <AnswerStream>  # 流式回答文本
│   │       └── <SourcesPanel>  # 折叠引用来源
│   └── <StatusBar>             # 工作流步骤可视化
├── <InputArea>
│   ├── <TextInput>             # 输入框
│   └── <SendButton>            # 发送按钮
└── <Sidebar> (移动端)           # 历史/来源抽屉
```

### 视觉风格

- **色调**: 极深灰黑 (`#0D0D0D` 主背景) + 冷调灰 (`#1A1A1A` 卡片) + 金色点缀 (`#C9A962`)
- **字体**: Noto Sans SC (中文) + Inter (英文)
- **卡片**: 圆角 12px，微弱边框 `rgba(255,255,255,0.05)` 背景
- **动效**: 淡入 + 微位移，duration 150-200ms，克制不过度
- **Status Bar**: 水平步骤条 + 图标，完成步骤变金色高亮
- **空状态**: 居中提示文案 + 法律图标

### 状态管理

React `useState` + `useReducer`，无需 Redux/Zustand。

### 响应式

- **桌面**: 主聊天区居中 + 两侧留白
- **平板/移动**: 单栏 + 底部抽屉切换来源/历史

### 中间步骤展示

Status Bar 实时显示：
1. 🔍 识别意图 → 2. 📚 检索知识 → 3. ✍️ 生成回答

---

## 4. 后端改动要点

| 文件 | 职责 |
|------|------|
| `backend/main.py` | FastAPI 初始化、CORS、中间件 |
| `backend/routers/chat.py` | `POST /api/chat` SSE 端点，调用 `ask_agent()` |
| `backend/routers/health.py` | `GET /api/health` |
| `backend/services/streamer.py` | SSE 事件发送器，按步骤 yield |
| `backend/config.py` | 复用 `src/config.py`，路径指向项目根目录 |

**SSE 实现**: `ask_agent()` 是同步阻塞调用，通过 `asyncio.to_thread()` 在后台线程执行，不阻塞事件循环。

---

## 5. 实施顺序

1. **后端骨架** — FastAPI 路由、SSE 服务、`backend/config.py`
2. **前后端联调** — 确保 SSE 事件流正确传递
3. **前端骨架** — Next.js 页面结构、API 客户端
4. **对话功能** — 流式消息渲染、Status Bar
5. **视觉美化** — 深色主题、动效、响应式
6. **About 页** — 项目介绍

---

## 6. 测试策略

- 后端 SSE 端点: `pytest` + `httpx` 测试流式响应
- 前端组件: Next.js 内置测试或 Playwright 端到端
- 核心逻辑: 复用现有 `tests/` 单元测试，不改动

import { Header } from "@/components/layout/Header";

export default function AboutPage() {
  return (
    <div className="flex flex-col min-h-screen bg-primary">
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

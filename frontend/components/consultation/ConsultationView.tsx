"use client";

import { useState } from "react";
import { agentEvents, citations, currentMatter, evidenceItems, messages } from "@/lib/data";
import { CitationChip, EvidencePanel } from "@/components/evidence/EvidencePanel";
import { MatterHeader, MatterOutlinePanel } from "@/components/matter/MatterHeader";

export function ConsultationView() {
  const [selectedEvidence, setSelectedEvidence] = useState("e1");
  const [draft, setDraft] = useState("");

  return (
    <div className="page-stack">
      <MatterHeader matter={currentMatter} />
      <div className="consultation-layout">
        <MatterOutlinePanel />

        <section className="conversation-panel">
          <div className="intake-card">
            <div>
              <div className="eyebrow">Structured intake</div>
              <h2>解除路径初步框架</h2>
              <p>
                系统已将问题拆解为事实固定、录用条件明示、考核对应性、通知程序和赔偿风险五个审查点。
              </p>
            </div>
            <span className="status-badge partial">Partial</span>
          </div>

          <div className="message-thread" aria-label="Consultation thread">
            {messages.map((message) => (
              <article className={`message ${message.role}`} key={message.id}>
                <div className="message-meta">
                  <strong>{message.role === "user" ? "User" : message.role === "assistant" ? "Lexiora" : "System"}</strong>
                  <span>{message.createdAt}</span>
                </div>
                <p>{message.content}</p>
                {message.citations ? (
                  <div className="chip-row">
                    {message.citations.map((citation) => (
                      <span onClick={() => setSelectedEvidence(citation.sourceId)} key={citation.id}>
                        <CitationChip label={citation.label} type={citation.type} />
                      </span>
                    ))}
                  </div>
                ) : null}
              </article>
            ))}
          </div>

          <section className="answer-grid">
            {[
              ["Issue summary", "试用期解除可以成立，但必须证明录用条件具体、已明示且考核结论可对应。"],
              ["Applicable law", "劳动合同法第 39 条是主要依据，地方裁判规则强化了证明责任。"],
              ["Supporting cases", "上海相关案例倾向审查书面录用条件、签收证明与绩效证据之间的闭环。"],
              ["Recommended next steps", "补充入职文件签收、岗位目标确认、考核规则送达和工会通知材料。"],
            ].map(([title, body]) => (
              <article className="answer-card" key={title}>
                <div>
                  <span className="status-badge draft">Draft</span>
                  <h3>{title}</h3>
                </div>
                <p>{body}</p>
                <div className="chip-row">
                  {citations.slice(0, 2).map((citation) => (
                    <CitationChip key={`${title}-${citation.id}`} label={citation.label} type={citation.type} />
                  ))}
                </div>
              </article>
            ))}
          </section>

          <form className="composer">
            <textarea
              aria-label="Follow-up question"
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Add facts, ask for a risk review, or request a structured draft..."
              value={draft}
            />
            <div className="composer-actions">
              <button className="button secondary" type="button">
                Attach
              </button>
              <button className="button primary" disabled={!draft.trim()} type="button">
                Send
              </button>
            </div>
          </form>
        </section>

        <aside className="right-rail">
          <EvidencePanel items={evidenceItems} selectedId={selectedEvidence} />
          <section className="panel">
            <div className="panel-title">Agent activity</div>
            <ol className="timeline">
              {agentEvents.map((event) => (
                <li className={event.status} key={event.name}>
                  <strong>{event.name}</strong>
                  <span>{event.message}</span>
                  <small>{event.elapsed}</small>
                </li>
              ))}
            </ol>
          </section>
          <section className="risk-panel">
            <strong>High uncertainty</strong>
            <p>录用条件明示证据不足时，违法解除风险显著升高。</p>
          </section>
        </aside>
      </div>
    </div>
  );
}

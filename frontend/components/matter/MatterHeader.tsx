import { matterTypeLabel, statusLabel } from "@/lib/status";
import type { MatterSummary } from "@/lib/types";

export function StatusBadge({ status }: { status: MatterSummary["status"] }) {
  return <span className={`status-badge ${status}`}>{statusLabel(status)}</span>;
}

export function MatterHeader({ matter }: { matter: MatterSummary }) {
  return (
    <section className="matter-header">
      <div>
        <div className="eyebrow">Matter status</div>
        <h1>{matter.title}</h1>
        <p>{matter.summary}</p>
      </div>
      <div className="matter-meta">
        <StatusBadge status={matter.status} />
        <span>{matterTypeLabel(matter.matterType)}</span>
        <span>{matter.jurisdiction}</span>
        <span>{matter.updatedAt}</span>
        <button className="button secondary" type="button">
          Save
        </button>
        <button className="button primary" type="button">
          Export
        </button>
      </div>
    </section>
  );
}

export function MatterOutlinePanel() {
  const sections = [
    ["Overview", "解除路径、事实背景、当前状态"],
    ["Facts", "3 个已固定事实，2 个待核实事实"],
    ["Issues", "录用条件明示、举证责任、程序完整性"],
    ["Authorities", "1 条法律、1 个案例、1 份材料"],
    ["Notes", "建议补充入职签收与考核规则送达"],
  ];

  return (
    <aside className="panel outline-panel">
      <div className="panel-title">Matter outline</div>
      {sections.map(([title, body]) => (
        <button className="outline-item" key={title} type="button">
          <strong>{title}</strong>
          <span>{body}</span>
        </button>
      ))}
    </aside>
  );
}

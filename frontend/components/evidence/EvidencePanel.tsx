import type { EvidenceItem } from "@/lib/types";

export function CitationChip({
  label,
  type,
}: {
  label: string;
  type: string;
}) {
  return (
    <button className={`citation-chip ${type}`} type="button">
      {label}
    </button>
  );
}

export function EvidenceSourceCard({
  item,
  selected,
}: {
  item: EvidenceItem;
  selected?: boolean;
}) {
  return (
    <button className={`source-card ${selected ? "selected" : ""}`} type="button">
      <span className="source-type">{item.type}</span>
      <strong>{item.title}</strong>
      <small>
        {item.authority} · {item.date}
      </small>
      <p>{item.excerpt}</p>
      <span className="confidence">{Math.round(item.relevanceScore * 100)}% relevance</span>
    </button>
  );
}

export function EvidencePanel({
  items,
  selectedId,
}: {
  items: EvidenceItem[];
  selectedId?: string;
}) {
  const selected = items.find((item) => item.id === selectedId) ?? items[0];

  return (
    <aside className="panel evidence-panel">
      <div className="panel-title">Verified sources</div>
      <div className="evidence-list compact">
        {items.map((item) => (
          <EvidenceSourceCard item={item} key={item.id} selected={item.id === selected.id} />
        ))}
      </div>
      <div className="source-viewer">
        <span className="source-type">{selected.type}</span>
        <h3>{selected.title}</h3>
        <dl className="metadata-grid">
          <div>
            <dt>Authority</dt>
            <dd>{selected.authority}</dd>
          </div>
          <div>
            <dt>Jurisdiction</dt>
            <dd>{selected.jurisdiction}</dd>
          </div>
          <div>
            <dt>Date</dt>
            <dd>{selected.date}</dd>
          </div>
          <div>
            <dt>Confidence</dt>
            <dd>{Math.round(selected.relevanceScore * 100)}%</dd>
          </div>
        </dl>
        <blockquote>{selected.excerpt}</blockquote>
        <div className="chip-row">
          {selected.relatedIssues.map((issue) => (
            <span className="tag" key={issue}>
              {issue}
            </span>
          ))}
        </div>
      </div>
    </aside>
  );
}

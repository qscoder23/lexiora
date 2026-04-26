import { AppShell } from "@/components/shell/AppShell";
import { adminMetrics } from "@/lib/data";

export default function AdminPage() {
  return (
    <AppShell active="Admin">
      <div className="page-stack">
        <section className="workspace-hero compact">
          <div>
            <div className="eyebrow">Admin</div>
            <h1>System and data health</h1>
            <p>Monitor ingestion, graph coverage, retrieval latency, and audit activity without leaving the product shell.</p>
          </div>
        </section>
        <section className="metrics-grid">
          {adminMetrics.map((metric) => (
            <article className="panel metric-card" key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
              <p>{metric.detail}</p>
            </article>
          ))}
        </section>
        <section className="panel">
          <div className="panel-title">Latest syncs</div>
          {["Labor law corpus refreshed", "Case index partial retry queued", "Graph relation extraction completed"].map((item) => (
            <div className="status-line success" key={item}>
              {item}
            </div>
          ))}
        </section>
      </div>
    </AppShell>
  );
}

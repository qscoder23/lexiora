import Link from "next/link";
import { AppShell } from "@/components/shell/AppShell";
import { matters } from "@/lib/data";
import { matterTypeLabel } from "@/lib/status";
import { StatusBadge } from "@/components/matter/MatterHeader";
import { routes } from "@/lib/routes";

export default function WorkspacePage() {
  return (
    <AppShell active="Workspace">
      <div className="page-stack">
        <section className="workspace-hero">
          <div>
            <div className="eyebrow">Workspace</div>
            <h1>Legal matters that stay grounded in evidence.</h1>
            <p>Start a structured consultation, inspect authorities, and keep matter history organized for long legal workflows.</p>
          </div>
          <Link className="button primary" href={routes.consultation()}>
            New matter
          </Link>
        </section>

        <div className="workspace-grid">
          <section className="panel wide-panel">
            <div className="section-heading">
              <div>
                <h2>Recent matters</h2>
                <p>Open a matter to continue consultation, evidence review, or structured analysis.</p>
              </div>
              <input className="inline-search" placeholder="Search matters..." />
            </div>
            <div className="matter-list">
              {matters.map((matter) => (
                <Link className="matter-card" href={routes.consultation(matter.id)} key={matter.id}>
                  <div>
                    <StatusBadge status={matter.status} />
                    <h3>{matter.title}</h3>
                    <p>{matter.summary}</p>
                  </div>
                  <div className="matter-card-meta">
                    <span>{matterTypeLabel(matter.matterType)}</span>
                    <span>{matter.jurisdiction}</span>
                    <span>{matter.updatedAt}</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          <aside className="side-stack">
            <section className="panel">
              <div className="panel-title">Templates</div>
              {["Labor termination review", "Contract risk memo", "Compliance issue map"].map((template) => (
                <button className="template-row" key={template} type="button">
                  {template}
                </button>
              ))}
            </section>
            <section className="panel">
              <div className="panel-title">Knowledge freshness</div>
              <div className="metric-large">92%</div>
              <p>Core legal corpus synced 18 minutes ago. Two ingestion jobs need review.</p>
            </section>
            <section className="panel">
              <div className="panel-title">System status</div>
              <div className="status-line success">Graph retrieval online</div>
              <div className="status-line warning">2 failed source imports</div>
            </section>
          </aside>
        </div>
      </div>
    </AppShell>
  );
}

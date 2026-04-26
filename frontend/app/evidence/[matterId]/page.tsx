import { EvidencePanel } from "@/components/evidence/EvidencePanel";
import { MatterHeader } from "@/components/matter/MatterHeader";
import { AppShell } from "@/components/shell/AppShell";
import { currentMatter, evidenceItems } from "@/lib/data";

export default function EvidencePage() {
  return (
    <AppShell active="Evidence">
      <div className="page-stack">
        <MatterHeader matter={currentMatter} />
        <div className="evidence-center">
          <section className="panel source-list-panel">
            <div className="section-heading">
              <div>
                <h2>Evidence center</h2>
                <p>Review law, cases, excerpts, and matter-specific source material.</p>
              </div>
              <div className="chip-row">
                <span className="tag">Relevance</span>
                <span className="tag">Authority strength</span>
              </div>
            </div>
            <div className="evidence-list">
              {evidenceItems.map((item) => (
                <article className="source-card static" key={item.id}>
                  <span className="source-type">{item.type}</span>
                  <h3>{item.title}</h3>
                  <small>{item.authority} · {item.date}</small>
                  <p>{item.excerpt}</p>
                </article>
              ))}
            </div>
          </section>
          <EvidencePanel items={evidenceItems} selectedId="e1" />
        </div>
      </div>
    </AppShell>
  );
}

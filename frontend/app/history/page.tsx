import Link from "next/link";
import { AppShell } from "@/components/shell/AppShell";
import { matters } from "@/lib/data";
import { StatusBadge } from "@/components/matter/MatterHeader";
import { routes } from "@/lib/routes";

export default function HistoryPage() {
  return (
    <AppShell active="History">
      <section className="panel">
        <div className="section-heading">
          <div>
            <h1>Session history</h1>
            <p>Browse, reopen, duplicate, and export previous legal matters.</p>
          </div>
          <input className="inline-search" placeholder="Filter saved matters..." />
        </div>
        <div className="history-table">
          {matters.map((matter) => (
            <Link className="history-row" href={routes.consultation(matter.id)} key={matter.id}>
              <strong>{matter.title}</strong>
              <span>{matter.jurisdiction}</span>
              <StatusBadge status={matter.status} />
              <span>{matter.updatedAt}</span>
            </Link>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

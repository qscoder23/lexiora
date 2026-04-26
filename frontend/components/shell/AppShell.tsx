import Link from "next/link";
import type { ReactNode } from "react";
import { primaryNavItems, routes } from "@/lib/routes";

export function AppShell({
  active,
  children,
}: {
  active: string;
  children: ReactNode;
}) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <Link className="brand" href={routes.workspace}>
          <span className="brand-mark">L</span>
          <span>
            <strong>Lexiora</strong>
            <small>Legal Intelligence</small>
          </span>
        </Link>

        <nav className="nav-list">
          {primaryNavItems.map((item) => (
            <Link
              aria-current={active === item.label ? "page" : undefined}
              className={`nav-item ${active === item.label ? "active" : ""}`}
              href={item.href}
              key={item.label}
            >
              <span className="nav-mark" aria-hidden="true">
                {item.mark}
              </span>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="profile-card">
          <span className="avatar" aria-hidden="true">
            LX
          </span>
          <span>
            <strong>Legal Ops</strong>
            <small>Shanghai workspace</small>
          </span>
        </div>
      </aside>

      <main className="shell-main">
        <header className="topbar">
          <label className="command-search">
            <span>⌘K</span>
            <input placeholder="Search matters, evidence, authorities..." />
          </label>
          <div className="topbar-actions">
            <button className="button ghost" type="button">
              Notifications
            </button>
            <Link className="button primary" href={routes.consultation()}>
              New matter
            </Link>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}

import { AppShell } from "@/components/shell/AppShell";

export default function SettingsPage() {
  return (
    <AppShell active="Settings">
      <section className="panel settings-panel">
        <div className="section-heading">
          <div>
            <h1>Settings</h1>
            <p>Adjust workspace preferences for density, evidence panels, and review defaults.</p>
          </div>
        </div>
        {["Compact density", "Keep evidence panel open", "Require risk review before export"].map((label, index) => (
          <label className="settings-row" key={label}>
            <span>
              <strong>{label}</strong>
              <small>{index === 0 ? "Use tighter spacing for long sessions." : "Persist this preference locally."}</small>
            </span>
            <input defaultChecked={index !== 0} type="checkbox" />
          </label>
        ))}
      </section>
    </AppShell>
  );
}

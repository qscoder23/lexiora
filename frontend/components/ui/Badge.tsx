import clsx from "clsx";

const DOMAIN_STYLES: Record<string, string> = {
  civil_law: "bg-accent-purple/15 text-accent-purple border-accent-purple/30",
  criminal_law: "bg-accent-red/15 text-accent-red border-accent-red/30",
  labor_law: "bg-accent-orange/15 text-accent-orange border-accent-orange/30",
  admin_law: "bg-accent-cyan/15 text-accent-cyan border-accent-cyan/30",
  general: "bg-text-secondary/15 text-text-secondary border-text-secondary/30",
};

const DOMAIN_ICONS: Record<string, string> = {
  civil_law: "⚖️",
  criminal_law: "🔨",
  labor_law: "📋",
  admin_law: "🏛️",
  general: "💬",
};

interface BadgeProps {
  domain: string;
  domain_zh: string;
}

export function DomainBadge({ domain, domain_zh }: BadgeProps) {
  const style = DOMAIN_STYLES[domain] ?? DOMAIN_STYLES.general;
  const icon = DOMAIN_ICONS[domain] ?? DOMAIN_ICONS.general;

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border",
        style
      )}
    >
      {icon} {domain_zh}
    </span>
  );
}

import type { MatterStatus } from "@/lib/types";

export function statusLabel(status: MatterStatus) {
  const labels: Record<MatterStatus, string> = {
    draft: "Draft",
    in_review: "In review",
    verified: "Verified",
    partial: "Partial",
    stale: "Stale source",
    error: "Needs attention",
  };
  return labels[status];
}

export function matterTypeLabel(type: string) {
  const labels: Record<string, string> = {
    contract: "Contract",
    labor: "Labor",
    corporate: "Corporate",
    tort: "Tort",
    compliance: "Compliance",
    general: "General",
  };
  return labels[type] ?? type;
}

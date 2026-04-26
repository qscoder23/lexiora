export const DEMO_MATTER_ID = "demo-matter";

export const routes = {
  home: "/",
  workspace: "/workspace",
  consultation: (matterId = DEMO_MATTER_ID) => `/consultation/${matterId}`,
  analysis: (matterId = DEMO_MATTER_ID) => `/analysis/${matterId}`,
  graph: (matterId = DEMO_MATTER_ID) => `/graph/${matterId}`,
  evidence: (matterId = DEMO_MATTER_ID) => `/evidence/${matterId}`,
  history: "/history",
  admin: "/admin",
  settings: "/settings",
} as const;

export const primaryNavItems = [
  { label: "Workspace", href: routes.workspace, mark: "W" },
  { label: "Consultation", href: routes.consultation(), mark: "C" },
  { label: "Analysis", href: routes.analysis(), mark: "A" },
  { label: "Graph", href: routes.graph(), mark: "G" },
  { label: "Evidence", href: routes.evidence(), mark: "E" },
  { label: "History", href: routes.history, mark: "H" },
  { label: "Admin", href: routes.admin, mark: "D" },
  { label: "Settings", href: routes.settings, mark: "S" },
];

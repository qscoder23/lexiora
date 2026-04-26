export type MatterStatus = "draft" | "in_review" | "verified" | "partial" | "stale" | "error";
export type MatterType = "contract" | "labor" | "corporate" | "tort" | "compliance" | "general";

export interface MatterSummary {
  id: string;
  title: string;
  matterType: MatterType;
  jurisdiction: string;
  status: MatterStatus;
  summary: string;
  updatedAt: string;
}

export interface CitationRef {
  id: string;
  type: "law" | "case" | "regulation" | "excerpt" | "graph_node";
  label: string;
  sourceId: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | "agent_event";
  content: string;
  createdAt: string;
  citations?: CitationRef[];
  streaming?: boolean;
}

export interface EvidenceItem {
  id: string;
  type: "statute" | "case" | "interpretation" | "policy" | "memo";
  title: string;
  authority: string;
  date: string;
  jurisdiction: string;
  excerpt: string;
  relevanceScore: number;
  relatedIssues: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: "law" | "case" | "issue" | "entity" | "behavior" | "responsibility";
  summary?: string;
  x: number;
  y: number;
}

export interface GraphEdge {
  id: string;
  from: string;
  to: string;
  label: string;
}

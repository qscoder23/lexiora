# 06. Data Contracts and State

## Frontend state domains

### 1. Auth and user preferences
- current user
- workspace
- theme
- density
- sidebar state

### 2. Matter state
- matter metadata
- matter summary
- matter status
- pinned items
- selected issue

### 3. Consultation state
- messages
- streaming answer chunks
- input draft
- upload status
- active agent events

### 4. Evidence state
- evidence list
- selected evidence item
- filters
- sort
- source preview state

### 5. Graph state
- nodes
- edges
- selected node
- graph filters
- depth
- loading state

## Suggested API shapes

### Matter summary
```ts
export interface MatterSummary {
  id: string
  title: string
  matterType: 'contract' | 'labor' | 'corporate' | 'tort' | 'compliance' | 'general'
  jurisdiction: string
  status: 'draft' | 'in_review' | 'verified' | 'partial' | 'stale' | 'error'
  summary: string
  updatedAt: string
}
```

### Chat message
```ts
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system' | 'agent_event'
  content: string
  createdAt: string
  citations?: CitationRef[]
  streaming?: boolean
}
```

### Citation ref
```ts
export interface CitationRef {
  id: string
  type: 'law' | 'case' | 'regulation' | 'excerpt' | 'graph_node'
  label: string
  sourceId: string
}
```

### Evidence item
```ts
export interface EvidenceItem {
  id: string
  type: 'statute' | 'case' | 'interpretation' | 'policy' | 'memo'
  title: string
  authority: string
  date: string
  jurisdiction: string
  excerpt: string
  relevanceScore: number
  relatedIssues: string[]
}
```

### Graph node
```ts
export interface GraphNode {
  id: string
  label: string
  type: 'law' | 'case' | 'issue' | 'entity' | 'behavior' | 'responsibility'
  summary?: string
}
```

## State management recommendations

### Use React Query for:
- fetching matter lists
- loading evidence
- graph data
- history lists
- admin metrics

### Use Zustand for:
- selected matter-local UI state
- drawer open/close
- selected citation
- graph filters
- density / layout mode

## Streaming behavior

- assistant answers should stream into a temporary message buffer
- agent events should stream separately from answer content
- errors during stream should preserve partial content

## Loading rules

- do not blank the whole page on refetch
- preserve prior data while fetching updates
- show skeletons only for first-load states

## Error handling

- consultation stream error: keep partial answer and show retry action
- evidence load error: preserve selected source context if possible
- graph load error: show retry inside canvas region, not full-screen block

## Persistence

Persist locally where helpful:
- sidebar collapsed state
- panel widths
- density preference
- last selected matter tab

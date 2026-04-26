# 05. Component Specifications

## Shell components

### AppSidebar
Props:
- activeRoute
- workspaceName
- items
- collapsed

States:
- default
- hover
- active
- collapsed

### TopCommandBar
Contains:
- command search
- quick create
- notifications
- profile menu

## Matter components

### MatterHeader
Fields:
- title
- matterType
- jurisdiction
- status
- lastUpdated
- actions

### MatterStatusBadge
Variants:
- draft
- in_review
- verified
- partial
- stale
- error

### MatterOutlinePanel
Sections:
- overview
- facts
- issues
- authorities
- notes

## Consultation components

### ChatMessage
Variants:
- user
- assistant
- system
- agent_event

Support:
- markdown rendering
- inline citation chips
- streaming state

### Composer
Features:
- textarea auto-resize
- attachment button
- send button
- enter to send / shift+enter newline
- disabled / loading / uploading states

### GeneratedAnswerCard
Sections:
- title
- status
- body
- citations
- actions

Actions:
- expand/collapse
- copy
- pin
- export
- view sources

### AgentTimeline
Displays:
- intake agent
- planner agent
- retriever agent
- reasoner agent
- review agent

Each item includes:
- name
- status
- elapsed time
- short message

## Evidence components

### CitationChip
Variants:
- law
- case
- regulation
- excerpt
- graph node

Behavior:
- click opens evidence drawer
- hover shows small preview tooltip

### EvidenceDrawer
Sections:
- source header
- metadata
- highlighted excerpt
- related issue tags
- pin/export actions

### EvidenceSourceCard
Fields:
- title
- sourceType
- authority
- date
- snippet
- relevance

## Analysis components

### FactCard
Fields:
- fact text
- source count
- confidence
- pinned state

### IssueCard
Fields:
- issue title
- summary
- relevant authorities
- evidence count
- confidence

### AuthorityBlock
Variants:
- statute
- judicial_interpretation
- case
- policy

Fields:
- title
- citation
- effective date
- jurisdiction
- excerpt

## Graph components

### GraphCanvas
Requirements:
- zoom and pan
- node selection
- relation highlight
- fit-to-screen
- legend toggle
- layout reset

### GraphFilterPanel
Controls:
- node type toggles
- relation toggles
- depth control
- confidence threshold

### NodeInspector
Fields:
- node name
- type
- summary
- linked authorities
- related nodes
- open evidence action

## Utility components

### EmptyState
Fields:
- title
- body
- primary action
- secondary action

### LoadingSkeleton
Variants:
- card
- panel
- thread
- table

### InlineStatus
Variants:
- loading
- success
- warning
- error
- partial

## Component quality bar

Every component must define:
- visual variants
- loading state
- empty state where applicable
- keyboard focus behavior
- truncation rules
- responsive rules

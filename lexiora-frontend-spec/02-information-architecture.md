# 02. Information Architecture

## Top-level app structure

- `/` Landing or auth redirect
- `/workspace` Main shell with recent matters and quick actions
- `/consultation/[matterId]` Main legal consultation workspace
- `/analysis/[matterId]` Structured case analysis page
- `/graph/[matterId]` GraphRAG exploration page
- `/evidence/[matterId]` Evidence center and source inspection
- `/history` Saved sessions and templates
- `/admin` System and data health console
- `/settings` Personal preferences and workspace settings

## Navigation model

### Global shell
Persistent left sidebar:
- logo / workspace switcher
- workspace
- consultation
- analysis
- graph
- evidence
- history
- admin
- settings
- user profile

### Matter-local context bar
Visible inside matter routes:
- matter title
- status badge
- jurisdiction
- last updated
- active agents / processing status
- export button
- save button

## Main user flow

### Flow 1: Start a new consultation
1. user enters workspace
2. clicks “New matter”
3. sees structured intake modal with optional freeform question
4. matter is created
5. lands in consultation page
6. system runs intake / routing / retrieval planning
7. answer streams while evidence panel populates

### Flow 2: Inspect answer support
1. user reads draft answer
2. clicks citation chip or evidence badge
3. evidence drawer opens on right
4. source text, authority type, and confidence metadata are shown
5. user may pin evidence to matter notes

### Flow 3: Move from chat to structured analysis
1. conversation establishes basic facts
2. user switches to analysis tab
3. facts, issues, laws, and cases are rendered into structured sections
4. user can manually edit facts or pin issues

### Flow 4: Explore graph relationships
1. user opens graph page
2. entity search and focal node appear on left
3. graph canvas in center
4. inspector panel on right
5. user can expand relations, filter node types, and inspect supporting materials

## Layout hierarchy

### Workspace page
- header
- search and quick actions
- recent matters grid/list
- suggested templates
- system status / knowledge freshness cards

### Consultation page
Three-column desktop layout:
- left: matter nav / pinned artifacts / outline
- center: conversation + generated answer blocks
- right: evidence drawer / agent activity / citations

### Analysis page
Two-column layout:
- main content: facts, issues, laws, cases, recommendations
- side panel: evidence links, risk markers, agent trace summary

### Graph page
Three-panel layout:
- left panel: filters and entity search
- center: graph canvas
- right panel: node detail inspector

### Evidence page
Two-pane document review layout:
- source list on left
- source viewer on right

## Empty states

Use elegant, text-first empty states with action prompts. Avoid cartoon illustrations.

Examples:
- “No matter selected. Start with a question or upload source material.”
- “No supporting evidence pinned yet.”
- “Expand a graph node to inspect linked authorities.”

## Error states

Should be quiet and explicit:
- what failed
- whether retry is available
- whether generated content may be incomplete

## IA constraints

- Conversation and evidence must never fully hide each other on desktop.
- Generated content must always show its status: draft, verified, partial, stale.
- The graph view should not become the default entry point for first-time users.

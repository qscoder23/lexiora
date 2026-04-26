# 04. Page Specifications

## A. Workspace Page

### Purpose
Central launchpad for recent matters, templates, and system readiness.

### Layout
- top header with title, global search, and new matter button
- two-row content grid
- left wide column for recent matters
- right narrow column for templates and system cards

### Sections
1. Welcome / title bar
2. Search matters
3. New matter CTA
4. Recent matters list
5. Pinned matters
6. Templates
7. Knowledge freshness card
8. Data ingestion / system status card

### Recent matter card
Must show:
- title
- short summary
- jurisdiction
- matter type
- updated time
- status badge
- quick open action

## B. Consultation Workspace

### Purpose
Primary experience for entering a legal question and receiving grounded output.

### Layout
Three columns on desktop.

#### Left column (280px)
- matter outline
- pinned facts
- pinned citations
- related tasks

#### Center column (fluid)
- conversation thread
- user input composer
- generated answer sections
- follow-up prompts

#### Right column (360px)
- evidence drawer
- citations
- agent activity timeline
- risk alerts

### Main blocks in center column
1. matter header
2. structured intake summary
3. conversation bubbles
4. generated answer cards
5. answer section toggles:
   - issue summary
   - applicable law
   - supporting cases
   - recommended next steps
6. input composer with attachments

### Interaction rules
- when user clicks a citation, right panel opens and scrolls to evidence
- when a new answer is streaming, keep scroll anchored unless user manually scrolls away
- agent activity should be visible but collapsible

## C. Analysis Page

### Purpose
Transform consultation output into a structured case analysis.

### Layout
Main content with sticky side inspector.

### Sections
1. Facts timeline
2. Parties and roles
3. Legal issues
4. Applicable authorities
5. Case comparisons
6. Preliminary conclusion
7. Risks and unknowns
8. Next-step recommendations

### UI details
- each section is a card block with edit / pin / cite actions
- issue cards may show confidence and supporting evidence count
- law sections differentiate statute vs judicial interpretation vs case

## D. Graph Explorer

### Purpose
Inspect legal entities and relationships surfaced by GraphRAG.

### Layout
Three panels.

#### Left panel
- search input
- filters for node types
- depth / relation controls
- graph legend

#### Center
- graph canvas
- zoom/pan controls
- focus mode

#### Right inspector
- selected node details
- summary
- relation list
- linked evidence
- open in evidence center action

### Graph rules
- default graph depth should be shallow to reduce clutter
- selected node must remain visually dominant
- allow hide/show node categories
- animate graph changes gently

## E. Evidence Center

### Purpose
Provide a quiet review environment for law, cases, excerpts, and citations.

### Layout
Split view.

#### Left
- evidence source list
- filter chips
- sort by relevance / recency / authority strength

#### Right
- source viewer
- excerpt highlights
- citation metadata
- pin/export controls

### Source card fields
- source title
- source type
- issuing authority / court
- date
- relevance score or confidence
- related issue tags

## F. History Page

### Purpose
Browse, reopen, duplicate, and export previous matters.

### Sections
- search and filters
- saved matters table/list
- saved templates
- starred items

## G. Admin Page

### Purpose
Give operators confidence that knowledge and retrieval systems are healthy.

### Sections
- ingestion pipeline status
- latest syncs
- graph coverage summary
- failed jobs
- model/tool latency cards
- audit log summary

### Note
Admin should visually align with the main product; avoid raw ops aesthetic unless intended.

# 07. Implementation Plan for Coding Agent

## Recommended stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide icons
- Framer Motion
- Zustand
- TanStack Query
- React Flow for graph explorer

## Suggested folder structure

```txt
src/
  app/
    workspace/
    consultation/[matterId]/
    analysis/[matterId]/
    graph/[matterId]/
    evidence/[matterId]/
    history/
    admin/
    settings/
  components/
    shell/
    matter/
    consultation/
    analysis/
    evidence/
    graph/
    ui/
  features/
    matters/
    consultation/
    evidence/
    graph/
    history/
    admin/
  lib/
    api/
    utils/
    formatters/
    constants/
  stores/
  hooks/
  styles/
```

## Build order

### Phase 1
- app shell
- sidebar
- top bar
- workspace page
- consultation page scaffold
- evidence drawer scaffold
- design tokens

### Phase 2
- generated answer cards
- citations
- matter outline
- history page
- analysis page

### Phase 3
- graph explorer
- advanced filters
- admin page
- polish and motion

## Tailwind token mapping
Create CSS variables first and expose semantic utility classes.

Examples:
- `--bg`
- `--surface`
- `--surface-elevated`
- `--border-subtle`
- `--text-primary`
- `--accent-primary`
- `--accent-secondary`

## Motion implementation guidance

Use Framer Motion only where motion improves comprehension:
- drawer open/close
- answer streaming reveal
- card enter transitions
- graph panel transitions

Do not animate every list item unnecessarily.

## Page acceptance criteria

### Workspace
- user can open a matter from recent list
- empty, loading, and populated states exist

### Consultation
- three-column layout on desktop
- citations open evidence panel
- streaming answer placeholder exists
- agent timeline exists

### Analysis
- structured legal sections rendered as cards
- editable facts/issues placeholders supported

### Graph
- graph canvas loads mock nodes and edges
- right inspector responds to selection
- filters affect graph presentation

### Evidence
- list/source split-view works
- excerpt highlights displayed clearly

## Implementation standard

- all major components typed
- all screens responsive down to tablet
- no hard-coded magic spacing without token mapping
- no overuse of gradients or shadows
- all interactive controls have hover/focus/disabled states

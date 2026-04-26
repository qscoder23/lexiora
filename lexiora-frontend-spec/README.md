# Lexiora Frontend Implementation Pack

This package is designed to be handed directly to Codex, Claude Code, or another coding agent to implement the frontend for **Lexiora**, a legal consultation assistant built on **multi-agent orchestration + GraphRAG**.

## Included files

- `01-product-and-ux-brief.md` — product positioning, UX goals, user roles, and core experience principles
- `02-information-architecture.md` — app structure, navigation, page hierarchy, and user flows
- `03-visual-design-system.md` — visual direction, tokens, typography, spacing, states, motion, and accessibility
- `04-page-specifications.md` — page-by-page UI specification and layout rules
- `05-component-specifications.md` — reusable components, props, states, and interaction behavior
- `06-data-contracts-and-state.md` — frontend state model, API shapes, edge cases, and loading patterns
- `07-implementation-plan-for-coding-agent.md` — recommended tech stack, folder structure, milestones, and acceptance criteria
- `08-prompt-for-codex-or-claude-code.md` — copy-paste prompt for implementation by a coding agent
- `09-copy-deck-and-microcopy.md` — UI copy guidelines and product language

## Recommended implementation target

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **UI:** React + Tailwind CSS + shadcn/ui
- **State:** Zustand + React Query
- **Charts/graph:** React Flow + lightweight charting lib
- **Animation:** Framer Motion

## Product posture

This is not a generic chatbot UI. It should feel like a **professional legal intelligence workspace**:

- calm and credible
- minimal but not cold
- visually fluid
- citation-first
- structured output over noisy conversation
- optimized for long-form analytical work

## Visual keywords

**Modern, restrained, premium, clean, deep-focus, trustworthy, high-clarity, low-noise.**

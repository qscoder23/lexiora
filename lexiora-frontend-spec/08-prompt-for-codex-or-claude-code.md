# 08. Prompt for Codex or Claude Code

Copy the following prompt into your coding assistant.

---

Build a polished frontend for a product named **Lexiora**, a legal consultation assistant that combines **multi-agent orchestration** and **GraphRAG**.

Use the attached markdown files as the source of truth and implement the UI accordingly.

## Technical requirements
- Use **Next.js 14+ App Router**
- Use **TypeScript**
- Use **Tailwind CSS**
- Use **shadcn/ui** for primitives where appropriate
- Use **Framer Motion** for subtle transitions
- Use **Zustand** for local UI state
- Use **TanStack Query** for async data
- Use **React Flow** for the graph explorer
- Use **Lucide** icons

## Product style requirements
- Visual style must be smooth, premium, calm, clean, and trustworthy
- The UI is for serious legal work, not a casual chatbot
- Keep the interface minimal, text-friendly, citation-first, and low-noise
- Avoid flashy AI aesthetics, bright gradients, glassmorphism, or decorative clutter

## Required routes
- /workspace
- /consultation/[matterId]
- /analysis/[matterId]
- /graph/[matterId]
- /evidence/[matterId]
- /history
- /admin
- /settings

## Required implementation tasks
1. Set up theme variables and core layout shell
2. Build sidebar and top command bar
3. Build workspace page with recent matters and templates
4. Build consultation page with three-column layout
5. Build evidence drawer and citation interactions
6. Build analysis page with structured legal sections
7. Build graph page with React Flow and right-side inspector
8. Build evidence page split view
9. Build history and admin pages
10. Add refined hover, focus, loading, and empty states

## Data requirements
Use mock typed data and mock API adapters first. Do not block implementation on backend availability.

## Quality bar
- Components must be reusable and typed
- Use semantic design tokens
- Ensure desktop-first layouts feel refined
- Add smooth but restrained animation
- Support loading, empty, and error states for all major screens
- Keep typography and spacing elegant and readable for long-form legal content

## Deliverables
- Full frontend codebase scaffold
- Reusable components
- Mock data layer
- Route pages
- Clean folder structure
- README with run instructions

Start by creating the app shell, theme tokens, and route scaffolds, then build the consultation workspace and evidence interactions first.

---

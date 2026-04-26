# 01. Product and UX Brief

## Product definition

**Lexiora** is a legal consultation and research assistant that combines **multi-agent orchestration** with **GraphRAG**. The frontend should support not just chat, but a structured legal workflow:

1. intake and problem framing
2. retrieval planning and evidence surfacing
3. legal issue decomposition
4. law/case/citation inspection
5. draft answer generation with risk review

The product should feel closer to a **legal intelligence console** than a consumer chat app.

## Core UX goals

### 1. Trust before delight
The interface must signal credibility immediately:
- clean information hierarchy
- restrained motion
- visible source citations
- clear boundaries between facts, retrieved evidence, and generated analysis

### 2. Structured over conversational
The main experience should allow rich conversation, but always expose structure:
- matter title
- facts
- issues
- applicable law
- supporting cases
- risk alerts
- final answer draft

### 3. Deep work support
Users may stay in the same matter for a long time. The UI must support:
- long sessions
- split-pane reading
- persistent evidence panel
- saved notes
- compact mode and focused mode

### 4. Low cognitive noise
Avoid dashboards overloaded with charts or flashy widgets. Prioritize:
- whitespace
- typography
- stable layout
- subtle grouping
- progressive disclosure

## Target users

### Primary
- legal tech product teams
- in-house legal ops
- paralegals and junior legal researchers
- startup founders seeking structured legal guidance

### Secondary
- law firms for internal knowledge workflows
- compliance teams
- contract reviewers

## Primary user jobs

- understand a legal issue quickly
- inspect the basis of the answer
- compare relevant authorities and cases
- track a matter from question to draft recommendation
- export a structured answer with references

## Experience principles

### A. Every answer should be inspectable
Every generated section should link to supporting evidence.

### B. Retrieval is visible
GraphRAG and multi-agent steps should be understandable without exposing raw system complexity.

### C. Risk is explicit
High-risk legal uncertainty must be highlighted rather than hidden.

### D. Reading experience matters
The product must be optimized for text-heavy workflows.

## Primary screens

1. Workspace / matter list
2. Consultation workspace
3. Case analysis view
4. Knowledge graph explorer
5. Evidence center
6. Session history
7. Admin / data health (optional but recommended)

## Responsive behavior priorities

### Desktop first
Primary implementation target should be desktop and laptop workflows.

### Tablet supported
Main panels should collapse cleanly into tabs or drawers.

### Mobile deferred
Mobile can support session browsing and lightweight consultation, but the initial implementation should not optimize for complex graph work.

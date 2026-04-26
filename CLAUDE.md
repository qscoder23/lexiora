# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lexiora is a Chinese legal consultation assistant built on Multi-Agent orchestration and GraphRAG. It supports multi-domain legal Q&A (civil, criminal, labor, administrative law) with knowledge graph retrieval and structured answer generation. Purpose: graduation thesis + graduate school interview showcase.

## Tech Stack

- **Language**: Python 3.11+
- **Package Manager**: uv
- **LLM**: DeepSeek V4 (via OpenAI-compatible API)
- **Embedding**: text-embedding-v3 (DashScope)
- **Agent Framework**: LangGraph (StateGraph for multi-agent orchestration)
- **Graph DB**: Neo4j Community Edition (Docker)
- **Vector Store**: FAISS
- **Web UI**: Streamlit
- **Config**: YAML (`config/settings.yaml`) with env var overrides

## Common Commands

```bash
# Install dependencies
uv sync

# Run tests (all)
uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_processor.py -v

# Run the Streamlit app
uv run streamlit run src/app/main.py

# Run import script (requires Neo4j running)
uv run python scripts/import_sample_data.py
```

## Required Environment Variables

- `DEEPSEEK_API_KEY` — DeepSeek API key (overrides config file)
- `DASHSCOPE_API_KEY` — DashScope API key for embeddings (overrides config file)
- `NEO4J_PASSWORD` — Neo4j password (overrides config file)

## Architecture

Four-layer architecture (bottom-up), with business logic strictly separated from UI:

```
Data Layer → GraphRAG Layer → Agent Layer → Interaction Layer
```

### Data Flow

```
User Question → Coordinator Agent (intent/domain identification)
  → Domain Agent (specialized Q&A)
    → GraphRAG (hybrid retrieval)
      → LLM generation
    → Reviewer Agent (quality check)
  → Response to User
```

### Key Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Config | `src/config.py` | Loads `config/settings.yaml`, merges env vars |
| Data Collection | `src/data/collector.py` | Downloads legal datasets, provides sample data |
| Data Processing | `src/data/processor.py` | Splits law text into law-chapter-article structure |
| Knowledge Graph | `src/data/kg_builder.py` | Builds Neo4j nodes/edges, MERGE-based Cypher |
| Vector Search | `src/retrieval/vector_search.py` | FAISS index build + similarity query via DashScope embeddings |
| Graph Search | `src/retrieval/graph_search.py` | LLM-based entity extraction → Cypher query → 2-hop traversal |
| Fusion | `src/retrieval/fusion.py` | Weighted merge of vector+graph results with dedup, `hybrid_search()` as main entry |
| RAG | `src/retrieval/rag.py` | Orchestrates retrieval → prompt construction → LLM call |
| Coordinator | `src/agents/coordinator.py` | Domain identification + LangGraph StateGraph definition + `ask_agent()` entry point |
| Domain Agent | `src/agents/domain_agent.py` | Shared base class, loads per-domain YAML config from `src/agents/config/` |
| Reviewer | `src/agents/reviewer.py` | Checks citation presence, citation accuracy, and disclaimer in answers |
| Streamlit UI | `src/app/main.py` | Display only — all logic lives in modules above |

### Agent Routing

The coordinator maps user input to one of 5 domains: `civil_law`, `criminal_law`, `labor_law`, `admin_law`, `general`. Each domain has a YAML prompt config in `src/agents/config/`. Unknown domains fall back to `general.yaml`.

## Design Principles

- **Logic/UI separation**: Streamlit does nothing but call `ask_agent()` and render — no business logic in `main.py`
- **Modularity**: Each module owns one responsibility; can be tested independently
- **Explainability**: Answers always cite law articles and cases; retrieval is traceable (critical for thesis defense)
- **Config-driven**: Agent prompts, retrieval weights, model params all live in YAML configs

## Neo4j Setup (Docker)

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5-community
```

## Design and Plan Docs

- Design spec: `docs/superpowers/specs/2026-04-16-lexiora-design.md`
- Implementation plan: `docs/superpowers/plans/2026-04-16-lexiora-implementation-plan.md`

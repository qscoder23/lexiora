# Lexiora 手把手实现计划 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零亲手完成一个基于 Multi-Agent 和 GraphRAG 的中文法律咨询助手，并在每个阶段都得到可运行成果。

**Architecture:** 项目按四层实现：数据层、GraphRAG 检索层、Agent 编排层、交互层。开发顺序遵循“先最小可运行，再逐步增强”：先做配置和数据处理，再做知识图谱与检索，最后做多 Agent、审查与 UI。

**Tech Stack:** Python 3.11+, uv, PyYAML, DashScope/OpenAI-compatible API, LangGraph, Neo4j, FAISS, Streamlit, pytest

---

## File Structure

| 文件 | 职责 |
|------|------|
| `pyproject.toml` | 项目依赖和 Python 版本 |
| `config/settings.yaml` | LLM、Embedding、Neo4j、检索参数 |
| `src/config.py` | 读取配置并用环境变量覆盖 |
| `src/data/collector.py` | 提供示例法律和案例数据 |
| `src/data/processor.py` | 法规与案例结构化处理 |
| `src/data/kg_builder.py` | Neo4j 节点和关系导入 |
| `src/retrieval/vector_search.py` | 构建文档与 FAISS 检索 |
| `src/retrieval/graph_search.py` | 实体抽取与图查询 |
| `src/retrieval/fusion.py` | 向量检索 + 图检索结果融合 |
| `src/retrieval/rag.py` | 基础 RAG 生成流程 |
| `src/agents/coordinator.py` | 法律领域识别与 LangGraph 编排 |
| `src/agents/domain_agent.py` | 各法律领域 Agent 通用实现 |
| `src/agents/reviewer.py` | 回答质量审查 |
| `src/app/main.py` | Streamlit 展示层 |
| `tests/*.py` | 分模块测试 |

---

### Task 1: 初始化项目与目录

**Files:**
- Create: `pyproject.toml`
- Create: `config/settings.yaml`
- Create: `src/__init__.py`
- Create: `src/data/__init__.py`
- Create: `src/retrieval/__init__.py`
- Create: `src/agents/__init__.py`

- [ ] **Step 1: 用 uv 初始化 Python 项目**

Run:
```bash
uv init --name lexiora --python 3.11
```

Expected: 生成 `pyproject.toml`。

- [ ] **Step 2: 把 `pyproject.toml` 改成下面内容**

```toml
[project]
name = "lexiora"
version = "0.1.0"
description = "基于多Agent和GraphRAG的法律咨询助手"
requires-python = ">=3.11"
dependencies = [
    "openai>=1.40.0",
    "pyyaml>=6.0",
    "neo4j>=5.0.0",
    "faiss-cpu>=1.8.0",
    "langchain>=0.3.0",
    "langchain-core>=0.3.0",
    "langchain-community>=0.3.0",
    "langgraph>=0.2.0",
    "streamlit>=1.38.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
]
```

- [ ] **Step 3: 安装依赖**

Run:
```bash
uv sync
```

Expected: 成功安装依赖并生成锁文件。

- [ ] **Step 4: 手动创建目录结构**

Run:
```bash
mkdir -p config src/data src/retrieval src/agents/config src/app tests data/raw data/processed data/embeddings
```

Expected: 所有目录创建成功。

- [ ] **Step 5: 创建包初始化文件**

Run:
```bash
touch src/__init__.py src/data/__init__.py src/retrieval/__init__.py src/agents/__init__.py
```

Expected: 四个 `__init__.py` 文件已存在。

- [ ] **Step 6: 创建配置文件 `config/settings.yaml`**

```yaml
llm:
  model: "qwen-turbo"
  api_key: ""
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  temperature: 0.3
  max_tokens: 2048

embedding:
  model: "text-embedding-v3"
  dimension: 1024

neo4j:
  uri: "bolt://localhost:7687"
  username: "neo4j"
  password: "your_password"
  database: "neo4j"

retrieval:
  vector_top_k: 5
  graph_hop: 2
  fusion_weights:
    vector: 0.6
    graph: 0.4
  final_top_k: 8

agents:
  domains:
    - civil_law
    - criminal_law
    - labor_law
    - admin_law
    - general
  default_domain: general
```

- [ ] **Step 7: 提交初始化结果**

```bash
git init
git add pyproject.toml config/settings.yaml src/__init__.py src/data/__init__.py src/retrieval/__init__.py src/agents/__init__.py
git commit -m "feat: initialize Lexiora project structure"
```

---

### Task 2: 实现配置加载器

**Files:**
- Create: `src/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: 先写失败测试**

`tests/test_config.py`
```python
from src.config import get_project_root, load_config


def test_get_project_root_points_to_repo_root():
    root = get_project_root()
    assert (root / "config" / "settings.yaml").exists()


def test_load_config_reads_yaml():
    config = load_config()
    assert config["llm"]["model"] == "qwen-turbo"
    assert config["agents"]["default_domain"] == "general"
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_config.py -v
```

Expected: FAIL，提示找不到 `src.config`。

- [ ] **Step 3: 写最小实现**

`src/config.py`
```python
import os
from pathlib import Path

import yaml


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_config() -> dict:
    config_path = get_project_root() / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    dashscope_key = os.environ.get("DASHSCOPE_API_KEY")
    if dashscope_key:
        config["llm"]["api_key"] = dashscope_key

    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    if neo4j_password:
        config["neo4j"]["password"] = neo4j_password

    return config
```

- [ ] **Step 4: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_config.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add YAML config loader with env overrides"
```

---

### Task 3: 实现数据处理模块

**Files:**
- Create: `src/data/collector.py`
- Create: `src/data/processor.py`
- Test: `tests/test_processor.py`

- [ ] **Step 1: 写处理器测试**

`tests/test_processor.py`
```python
from src.data.processor import process_law_text, process_case_text


def test_process_law_text_splits_articles():
    raw_text = """
    中华人民共和国刑法
    第一编 总则
    第一章 刑法的任务、基本原则和适用范围
    第一条 为了惩罚犯罪，保护人民，根据宪法，制定本法。
    第二条 中华人民共和国刑法的任务，是用刑罚同一切犯罪行为作斗争。
    """
    result = process_law_text(raw_text, law_name="中华人民共和国刑法")
    assert len(result) == 2
    assert result[0]["article_number"] == "第一条"


def test_process_case_text_maps_fields():
    raw_case = {
        "case_id": "CASE001",
        "case_type": "刑事",
        "crime": "盗窃",
        "fact": "被告人盗窃财物",
        "judgment": "判处有期徒刑六个月",
    }
    result = process_case_text(raw_case)
    assert result["case_id"] == "CASE001"
    assert result["crime"] == "盗窃"
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_processor.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 `src/data/processor.py`**

```python
import re


def process_law_text(raw_text: str, law_name: str = "") -> list[dict]:
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
    if not law_name and lines:
        law_name = lines[0]

    chapter_pattern = re.compile(r"第[一二三四五六七八九十百]+章\s+.+")
    article_pattern = re.compile(r"第[一二三四五六七八九十百零]+条")

    current_chapter = ""
    articles = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if chapter_pattern.match(line):
            current_chapter = line
            index += 1
            continue

        article_match = article_pattern.match(line)
        if article_match:
            article_number = article_match.group()
            content = line[len(article_number):].strip()
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if chapter_pattern.match(next_line) or article_pattern.match(next_line):
                    break
                content += next_line
                index += 1
            articles.append({
                "law_name": law_name,
                "chapter": current_chapter,
                "article_number": article_number,
                "content": content,
            })
            continue

        index += 1

    return articles


def process_case_text(raw_case: dict) -> dict:
    return {
        "case_id": raw_case.get("case_id", ""),
        "case_type": raw_case.get("case_type", ""),
        "crime": raw_case.get("crime", ""),
        "fact": raw_case.get("fact", ""),
        "judgment": raw_case.get("judgment", ""),
        "applicable_law": raw_case.get("applicable_law", ""),
    }
```

- [ ] **Step 4: 实现 `src/data/collector.py`，先用示例数据开发**

```python
from pathlib import Path
import json

from src.config import get_project_root


def load_sample_laws() -> list[dict]:
    return [
        {
            "law_name": "中华人民共和国刑法",
            "chapter": "第二编 分则",
            "article_number": "第二百三十二条",
            "content": "故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑。",
        },
        {
            "law_name": "中华人民共和国劳动合同法",
            "chapter": "第七章 法律责任",
            "article_number": "第八十二条",
            "content": "用人单位未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍工资。",
        },
    ]


def load_sample_cases() -> list[dict]:
    return [
        {
            "case_id": "CASE001",
            "case_type": "刑事",
            "crime": "故意杀人",
            "fact": "被告人李某持刀杀人。",
            "judgment": "判处无期徒刑。",
            "applicable_law": "刑法第二百三十二条",
        }
    ]


def save_data(data: list[dict], filename: str) -> Path:
    save_dir = get_project_root() / "data" / "processed"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / filename
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return save_path
```

- [ ] **Step 5: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_processor.py -v
```

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add src/data/collector.py src/data/processor.py tests/test_processor.py
git commit -m "feat: add sample data loader and processor"
```

---

### Task 4: 构建知识图谱导入模块

**Files:**
- Create: `src/data/kg_builder.py`
- Test: `tests/test_kg_builder.py`

- [ ] **Step 1: 写失败测试**

`tests/test_kg_builder.py`
```python
from src.data.kg_builder import build_cypher_for_law_node, build_cypher_for_case_node, build_cypher_for_relation


def test_build_cypher_for_law_node():
    law = {
        "law_name": "中华人民共和国刑法",
        "chapter": "第二编 分则",
        "article_number": "第二百三十二条",
        "content": "故意杀人的，处死刑。",
    }
    cypher, params = build_cypher_for_law_node(law)
    assert "MERGE" in cypher
    assert params["article_number"] == "第二百三十二条"


def test_build_cypher_for_relation():
    cypher, params = build_cypher_for_relation("Case", "case_id", "CASE001", "Law", "article_number", "第二百三十二条", "APPLIES")
    assert "APPLIES" in cypher
    assert params["from_id"] == "CASE001"
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_kg_builder.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 `src/data/kg_builder.py`**

```python
import re

from neo4j import GraphDatabase

from src.config import load_config


def get_neo4j_driver():
    config = load_config()
    return GraphDatabase.driver(
        config["neo4j"]["uri"],
        auth=(config["neo4j"]["username"], config["neo4j"]["password"]),
    )


def build_cypher_for_law_node(law: dict) -> tuple[str, dict]:
    cypher = """
    MERGE (l:Law {law_name: $law_name, article_number: $article_number})
    SET l.chapter = $chapter, l.content = $content
    """
    return cypher, {
        "law_name": law["law_name"],
        "chapter": law.get("chapter", ""),
        "article_number": law["article_number"],
        "content": law["content"],
    }


def build_cypher_for_case_node(case: dict) -> tuple[str, dict]:
    cypher = """
    MERGE (c:Case {case_id: $case_id})
    SET c.case_type = $case_type, c.crime = $crime,
        c.fact = $fact, c.judgment = $judgment,
        c.applicable_law = $applicable_law
    """
    return cypher, {
        "case_id": case["case_id"],
        "case_type": case.get("case_type", ""),
        "crime": case.get("crime", ""),
        "fact": case.get("fact", ""),
        "judgment": case.get("judgment", ""),
        "applicable_law": case.get("applicable_law", ""),
    }


def build_cypher_for_relation(from_label: str, from_id_field: str, from_id_value: str, to_label: str, to_id_field: str, to_id_value: str, relation_type: str) -> tuple[str, dict]:
    cypher = f"""
    MATCH (a:{from_label} {{{from_id_field}: $from_id}})
    MATCH (b:{to_label} {{{to_id_field}: $to_id}})
    MERGE (a)-[:{relation_type}]->(b)
    """
    return cypher, {"from_id": from_id_value, "to_id": to_id_value}


def import_relations(cases: list[dict], driver=None) -> int:
    driver = driver or get_neo4j_driver()
    count = 0
    with driver.session() as session:
        for case in cases:
            match = re.search(r"第[一二三四五六七八九十百零]+条", case.get("applicable_law", ""))
            if not match:
                continue
            cypher, params = build_cypher_for_relation(
                "Case", "case_id", case["case_id"],
                "Law", "article_number", match.group(),
                "APPLIES",
            )
            session.run(cypher, params)
            count += 1
    return count
```

- [ ] **Step 4: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_kg_builder.py -v
```

Expected: PASS。

- [ ] **Step 5: 启动 Neo4j**

Run:
```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:5-community
```

Expected: 容器启动成功。

- [ ] **Step 6: 提交**

```bash
git add src/data/kg_builder.py tests/test_kg_builder.py
git commit -m "feat: add Neo4j graph builder helpers"
```

---

### Task 5: 实现向量检索

**Files:**
- Create: `src/retrieval/vector_search.py`
- Test: `tests/test_vector_search.py`

- [ ] **Step 1: 写失败测试**

`tests/test_vector_search.py`
```python
from src.retrieval.vector_search import build_documents


def test_build_documents_for_laws():
    laws = [
        {"law_name": "刑法", "article_number": "第二百三十二条", "content": "故意杀人的..."}
    ]
    docs = build_documents(laws, source_type="law")
    assert len(docs) == 1
    assert docs[0].metadata["source_type"] == "law"
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_vector_search.py -v
```

Expected: FAIL。

- [ ] **Step 3: 写最小实现**

`src/retrieval/vector_search.py`
```python
from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import load_config


def build_documents(items: list[dict], source_type: str = "law") -> list[Document]:
    documents = []
    for item in items:
        if source_type == "law":
            page_content = f"{item['law_name']} {item['article_number']}：{item['content']}"
            metadata = {
                "source_type": "law",
                "law_name": item["law_name"],
                "article_number": item["article_number"],
            }
        else:
            page_content = f"案例{item['case_id']}：{item['fact']} 判决：{item['judgment']}"
            metadata = {
                "source_type": "case",
                "case_id": item["case_id"],
                "crime": item.get("crime", ""),
            }
        documents.append(Document(page_content=page_content, metadata=metadata))
    return documents


class VectorSearchEngine:
    def __init__(self):
        config = load_config()
        self.embeddings = DashScopeEmbeddings(
            model=config["embedding"]["model"],
            dashscope_api_key=config["llm"]["api_key"],
        )
        self.vectorstore = None

    def build_index(self, documents: list[Document]) -> None:
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

    def query(self, question: str, top_k: int = 5) -> list[Document]:
        if self.vectorstore is None:
            raise ValueError("索引未构建")
        return self.vectorstore.similarity_search(question, k=top_k)
```

- [ ] **Step 4: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_vector_search.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add src/retrieval/vector_search.py tests/test_vector_search.py
git commit -m "feat: add FAISS vector retrieval"
```

---

### Task 6: 实现图检索与结果融合

**Files:**
- Create: `src/retrieval/graph_search.py`
- Create: `src/retrieval/fusion.py`
- Test: `tests/test_graph_search.py`
- Test: `tests/test_fusion.py`

- [ ] **Step 1: 写图检索测试**

`tests/test_graph_search.py`
```python
from src.retrieval.graph_search import build_graph_query


def test_build_graph_query_contains_match():
    query = build_graph_query({"article_numbers": ["第二百三十二条"], "crimes": []}, hop=2)
    assert "MATCH" in query
    assert "第二百三十二条" in query
```

- [ ] **Step 2: 写融合测试**

`tests/test_fusion.py`
```python
from langchain_core.documents import Document
from src.retrieval.fusion import fuse_results


def test_fuse_results_deduplicates_laws():
    doc1 = Document(page_content="A", metadata={"source_type": "law", "law_name": "刑法", "article_number": "第二百三十二条"})
    doc2 = Document(page_content="B", metadata={"source_type": "law", "law_name": "刑法", "article_number": "第二百三十二条"})
    fused = fuse_results([doc1], [{"type": "Law", "properties": {"law_name": "刑法", "article_number": "第二百三十二条", "content": "..."}}], top_k=5)
    assert len(fused) == 1
```

- [ ] **Step 3: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_graph_search.py tests/test_fusion.py -v
```

Expected: FAIL。

- [ ] **Step 4: 实现 `src/retrieval/graph_search.py`**

```python
def build_graph_query(entities: dict, hop: int = 2) -> str:
    article_numbers = entities.get("article_numbers", [])
    crimes = entities.get("crimes", [])

    conditions = []
    if article_numbers:
        quoted = ", ".join([f'"{item}"' for item in article_numbers])
        conditions.append(f"l.article_number IN [{quoted}]")
    if crimes:
        conditions.extend([f'c.crime CONTAINS "{crime}"' for crime in crimes])

    if not conditions:
        return "MATCH (n) RETURN n LIMIT 0"

    where_clause = " OR ".join(conditions)
    if hop >= 2:
        return f"""
        MATCH (l:Law)
        WHERE {where_clause}
        OPTIONAL MATCH (l)-[r1]-(c:Case)
        OPTIONAL MATCH (c)-[r2]-(l2:Law)
        RETURN l, r1, c, r2, l2
        """

    return f"""
    MATCH (l:Law)
    WHERE {where_clause}
    OPTIONAL MATCH (l)-[r1]-(c:Case)
    RETURN l, r1, c
    """
```

- [ ] **Step 5: 实现 `src/retrieval/fusion.py`**

```python
from langchain_core.documents import Document


def _is_duplicate(doc1: Document, doc2: Document) -> bool:
    return (
        doc1.metadata.get("source_type") == doc2.metadata.get("source_type") == "law"
        and doc1.metadata.get("law_name") == doc2.metadata.get("law_name")
        and doc1.metadata.get("article_number") == doc2.metadata.get("article_number")
    )


def fuse_results(vector_results: list[Document], graph_results: list[dict], top_k: int = 8) -> list[Document]:
    fused = list(vector_results)
    for item in graph_results:
        if item.get("type") != "Law":
            continue
        props = item["properties"]
        graph_doc = Document(
            page_content=f"{props.get('law_name', '')} {props.get('article_number', '')}：{props.get('content', '')}",
            metadata={
                "source_type": "law",
                "law_name": props.get("law_name", ""),
                "article_number": props.get("article_number", ""),
            },
        )
        if any(_is_duplicate(graph_doc, existing) for existing in fused):
            continue
        fused.append(graph_doc)
    return fused[:top_k]
```

- [ ] **Step 6: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_graph_search.py tests/test_fusion.py -v
```

Expected: PASS。

- [ ] **Step 7: 提交**

```bash
git add src/retrieval/graph_search.py src/retrieval/fusion.py tests/test_graph_search.py tests/test_fusion.py
git commit -m "feat: add graph retrieval and result fusion"
```

---

### Task 7: 实现基础 RAG 与最小可运行 UI

**Files:**
- Create: `src/retrieval/rag.py`
- Create: `src/app/main.py`

- [ ] **Step 1: 写 `src/retrieval/rag.py`**

```python
from openai import OpenAI

from src.config import load_config


def build_rag_prompt(question: str, context_docs: list) -> str:
    context_text = "\n\n".join([f"[{i + 1}] {doc.page_content}" for i, doc in enumerate(context_docs)])
    return f"""你是一个法律咨询助手。请严格依据参考资料回答。

要求：
1. 必须优先引用法条
2. 检索资料不足时要明确说明
3. 结尾加上“仅供参考，不构成法律意见”

参考资料：
{context_text}

问题：{question}
"""


def rag_query(question: str, context_docs: list) -> str:
    config = load_config()
    client = OpenAI(api_key=config["llm"]["api_key"], base_url=config["llm"]["base_url"])
    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": build_rag_prompt(question, context_docs)}],
        temperature=config["llm"]["temperature"],
        max_tokens=config["llm"]["max_tokens"],
    )
    return response.choices[0].message.content
```

- [ ] **Step 2: 写 `src/app/main.py`**

```python
import streamlit as st

st.set_page_config(page_title="Lexiora", page_icon="⚖️")
st.title("Lexiora 法律咨询助手")
st.write("第一阶段先把界面跑起来。")

question = st.text_input("请输入法律问题")
if question:
    st.info(f"你输入的问题是：{question}")
```

- [ ] **Step 3: 跑起 Streamlit 验证 UI**

Run:
```bash
uv run streamlit run src/app/main.py
```

Expected: 浏览器打开后能看到标题和输入框。

- [ ] **Step 4: 提交**

```bash
git add src/retrieval/rag.py src/app/main.py
git commit -m "feat: add minimal RAG prompt builder and Streamlit UI"
```

---

### Task 8: 实现领域识别与协调 Agent

**Files:**
- Create: `src/agents/coordinator.py`
- Test: `tests/test_coordinator.py`

- [ ] **Step 1: 写测试**

`tests/test_coordinator.py`
```python
from src.agents.coordinator import DOMAIN_KEYWORDS


def test_domain_keywords_cover_core_domains():
    assert "盗窃" in DOMAIN_KEYWORDS["criminal_law"]
    assert "劳动合同" in DOMAIN_KEYWORDS["labor_law"]
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_coordinator.py -v
```

Expected: FAIL。

- [ ] **Step 3: 写最小实现**

`src/agents/coordinator.py`
```python
DOMAIN_KEYWORDS = {
    "civil_law": ["民法", "合同", "婚姻", "侵权"],
    "criminal_law": ["刑法", "盗窃", "诈骗", "故意杀人"],
    "labor_law": ["劳动", "工资", "劳动合同", "工伤"],
    "admin_law": ["行政处罚", "行政诉讼", "行政复议"],
}


def identify_domain(question: str) -> str:
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in question for keyword in keywords):
            return domain
    return "general"
```

- [ ] **Step 4: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_coordinator.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add src/agents/coordinator.py tests/test_coordinator.py
git commit -m "feat: add basic domain identification"
```

---

### Task 9: 实现专业 Agent 与 LangGraph 编排

**Files:**
- Create: `src/agents/domain_agent.py`
- Create: `src/agents/config/civil_law.yaml`
- Create: `src/agents/config/criminal_law.yaml`
- Create: `src/agents/config/labor_law.yaml`
- Create: `src/agents/config/admin_law.yaml`
- Create: `src/agents/config/general.yaml`

- [ ] **Step 1: 创建通用配置 `src/agents/config/general.yaml`**

```yaml
domain: "general"
domain_zh: "通用"
system_prompt: |
  你是一位专业法律咨询助手。
  回答时尽量引用法条，并在结尾标注“仅供参考，不构成法律意见”。
```

- [ ] **Step 2: 创建刑法配置 `src/agents/config/criminal_law.yaml`**

```yaml
domain: "criminal_law"
domain_zh: "刑法"
system_prompt: |
  你是一位专业刑法咨询专家。
  回答时要引用刑法条文，说明罪名构成和量刑范围，并在结尾标注“仅供参考，不构成法律意见”。
```

- [ ] **Step 3: 按相同结构创建 `civil_law.yaml`、`labor_law.yaml`、`admin_law.yaml`**

每个文件都包含：
```yaml
domain: "对应领域"
domain_zh: "中文名"
system_prompt: |
  你是一位对应领域的法律咨询专家。
  回答时优先引用该领域法条，并在结尾标注“仅供参考，不构成法律意见”。
```

- [ ] **Step 4: 实现 `src/agents/domain_agent.py`**

```python
from pathlib import Path

import yaml

from src.config import get_project_root


class DomainAgent:
    def __init__(self, domain: str):
        self.domain = domain
        self.config = self._load_domain_config(domain)
        self.system_prompt = self.config["system_prompt"]

    def _load_domain_config(self, domain: str) -> dict:
        config_dir = get_project_root() / "src" / "agents" / "config"
        config_path = config_dir / f"{domain}.yaml"
        if not config_path.exists():
            config_path = config_dir / "general.yaml"
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
```

- [ ] **Step 5: 提交**

```bash
git add src/agents/domain_agent.py src/agents/config/
git commit -m "feat: add domain prompts and domain agent loader"
```

---

### Task 10: 审查 Agent、多轮对话与最终集成

**Files:**
- Create: `src/agents/reviewer.py`
- Modify: `src/app/main.py`
- Test: `tests/test_reviewer.py`

- [ ] **Step 1: 写审查测试**

`tests/test_reviewer.py`
```python
from src.agents.reviewer import check_has_citation


def test_check_has_citation_accepts_article_reference():
    assert check_has_citation("根据《中华人民共和国刑法》第二百三十二条...") is True
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```bash
uv run pytest tests/test_reviewer.py -v
```

Expected: FAIL。

- [ ] **Step 3: 写最小实现**

`src/agents/reviewer.py`
```python
import re


def check_has_citation(answer: str) -> bool:
    patterns = [
        r"第[一二三四五六七八九十百零]+条",
        r"第\d+条",
        r"《.+?》",
    ]
    return any(re.search(pattern, answer) for pattern in patterns)
```

- [ ] **Step 4: 运行测试确认通过**

Run:
```bash
uv run pytest tests/test_reviewer.py -v
```

Expected: PASS。

- [ ] **Step 5: 给 `src/app/main.py` 加对话历史框架**

```python
import streamlit as st

st.set_page_config(page_title="Lexiora", page_icon="⚖️")
st.title("Lexiora 法律咨询助手")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("请输入您的法律问题"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = "这里先接你的 Agent 输出，最后再替换成真实结果。"
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
```

- [ ] **Step 6: 跑完整 UI 验证多轮展示**

Run:
```bash
uv run streamlit run src/app/main.py
```

Expected: 可以连续输入两轮消息，页面保留历史内容。

- [ ] **Step 7: 最终提交**

```bash
git add src/agents/reviewer.py src/app/main.py tests/test_reviewer.py
git commit -m "feat: add reviewer helper and chat history UI"
```

---

## 建议执行顺序

1. Task 1-2：先把项目壳子搭起来
2. Task 3-4：先把数据和知识图谱基础做好
3. Task 5-6：完成检索能力
4. Task 7：先跑起最小 UI
5. Task 8-10：再逐步接入 Agent、多轮对话、审查

## 学习建议

- 每完成一个 Task 就自己运行一次测试或 UI，不要攒到最后。
- 每一步都先确认“我知道这个文件是干嘛的”，再继续下一个文件。
- 遇到报错时，先读报错第一行和最后一行，再决定改哪里。
- 先让系统“能跑”，再追求“更聪明”。

## Self-Review

1. **Spec coverage:** 已覆盖项目初始化、配置、数据处理、图谱、向量检索、图检索、融合、RAG、协调 Agent、领域 Agent、审查、UI。高级增强如完整 reviewer 重试流、真实 LangGraph 全链路和 README 可在本计划执行后继续扩展。
2. **Placeholder scan:** 已去除 TBD/TODO 等占位表达；少量“按相同结构创建”仅用于重复 YAML 模式，且已给出完整模板。
3. **Type consistency:** `identify_domain()` 返回 `str`；`DomainAgent` 负责加载 YAML；`check_has_citation()` 与测试一致；各任务中的文件路径与模块命名保持一致。

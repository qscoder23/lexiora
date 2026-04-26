# Lexiora 法律咨询助手 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于多Agent和GraphRAG的综合法律咨询助手，支持多领域法律问答、知识图谱检索、结构化回答生成。

**Architecture:** 四层架构（数据层 → GraphRAG层 → Agent层 → 交互层）。业务逻辑与UI严格分离，便于未来迁移。三阶段渐进交付，每阶段产出可运行成果。

**Tech Stack:** Python 3.11+, uv, 通义千问 (DashScope SDK), LangGraph, Neo4j, FAISS, Streamlit

**设计文档:** `docs/superpowers/specs/2026-04-16-lexiora-design.md`

---

## File Structure

| 文件 | 职责 |
|------|------|
| `pyproject.toml` | uv项目配置和依赖声明 |
| `config/settings.yaml` | API密钥、模型参数、数据库连接等配置 |
| `src/__init__.py` | 包初始化 |
| `src/config.py` | 配置加载工具，读取settings.yaml |
| `src/data/__init__.py` | 包初始化 |
| `src/data/collector.py` | 数据采集：下载公开法律法规和案例数据集 |
| `src/data/processor.py` | 数据处理：将原始数据结构化为统一JSON格式 |
| `src/data/kg_builder.py` | 知识图谱构建：实体关系抽取并写入Neo4j |
| `src/retrieval/__init__.py` | 包初始化 |
| `src/retrieval/vector_search.py` | 向量检索：FAISS索引构建和相似度查询 |
| `src/retrieval/graph_search.py` | 图检索：Neo4j Cypher查询和实体抽取 |
| `src/retrieval/fusion.py` | 结果融合：向量+图双路检索结果合并排序 |
| `src/retrieval/rag.py` | RAG核心：串联检索与LLM生成 |
| `src/agents/__init__.py` | 包初始化 |
| `src/agents/coordinator.py` | 协调Agent：意图识别和领域路由 |
| `src/agents/domain_agent.py` | 专业Agent基类：可复用的领域问答Agent |
| `src/agents/reviewer.py` | 审查Agent：回答质量校验 |
| `src/agents/config/civil_law.yaml` | 民法Agent prompt配置 |
| `src/agents/config/criminal_law.yaml` | 刑法Agent prompt配置 |
| `src/agents/config/labor_law.yaml` | 劳动法Agent prompt配置 |
| `src/agents/config/admin_law.yaml` | 行政法Agent prompt配置 |
| `src/agents/config/general.yaml` | 通用Agent prompt配置 |
| `src/app/main.py` | Streamlit入口：仅做展示，调用逻辑层 |
| `tests/test_processor.py` | 数据处理模块测试 |
| `tests/test_vector_search.py` | 向量检索模块测试 |
| `tests/test_graph_search.py` | 图检索模块测试 |
| `tests/test_fusion.py` | 结果融合模块测试 |
| `tests/test_coordinator.py` | 协调Agent测试 |
| `tests/test_domain_agent.py` | 专业Agent测试 |
| `tests/test_reviewer.py` | 审查Agent测试 |

---

## Task 1: 项目初始化

**Files:**
- Create: `pyproject.toml`
- Create: `config/settings.yaml`
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `src/data/__init__.py`
- Create: `src/retrieval/__init__.py`
- Create: `src/agents/__init__.py`

- [ ] **Step 1: 使用uv初始化项目**

在项目根目录执行：

```bash
uv init --name lexiora --python 3.11
```

- [ ] **Step 2: 编辑pyproject.toml，添加依赖**

```toml
[project]
name = "lexiora"
version = "0.1.0"
description = "基于多Agent和GraphRAG的法律咨询助手"
requires-python = ">=3.11"
dependencies = [
    "dashscope>=1.20.0",
    "langchain>=0.3.0",
    "langchain-community>=0.3.0",
    "langgraph>=0.2.0",
    "neo4j>=5.0.0",
    "faiss-cpu>=1.7.0",
    "pyyaml>=6.0",
    "streamlit>=1.38.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
]
```

- [ ] **Step 3: 安装依赖**

```bash
uv sync
```

- [ ] **Step 4: 创建目录结构和__init__.py文件**

```bash
mkdir -p config src/data src/retrieval src/agents/config src/app tests data/raw data/processed data/embeddings
touch src/__init__.py src/data/__init__.py src/retrieval/__init__.py src/agents/__init__.py
```

- [ ] **Step 5: 创建配置文件config/settings.yaml**

```yaml
llm:
  model: "qwen-turbo"
  api_key: ""  # 从环境变量 DASHSCOPE_API_KEY 读取
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  temperature: 0.7
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
    - "civil_law"
    - "criminal_law"
    - "labor_law"
    - "admin_law"
    - "general"
  default_domain: "general"
```

- [ ] **Step 6: 创建src/config.py**

```python
import os
from pathlib import Path

import yaml


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def load_config() -> dict:
    config_path = get_project_root() / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # 从环境变量覆盖API Key
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if api_key:
        config["llm"]["api_key"] = api_key
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "")
    if neo4j_password:
        config["neo4j"]["password"] = neo4j_password
    return config
```

- [ ] **Step 7: 验证环境——调用通义千问API**

创建临时验证脚本 `verify_env.py`（验证后删除）：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

response = client.chat.completions.create(
    model="qwen-turbo",
    messages=[{"role": "user", "content": "你好，请用一句话介绍你自己"}],
)
print(response.choices[0].message.content)
```

运行：

```bash
export DASHSCOPE_API_KEY="你的key"
uv run python verify_env.py
```

预期输出：通义千问的自我介绍。验证成功后删除 `verify_env.py`。

- [ ] **Step 8: 初始化git仓库并首次提交**

```bash
git init
git add pyproject.toml config/ src/ tests/ data/
git commit -m "feat: project initialization with uv, config, and directory structure"
```

---

## Task 2: 数据采集与处理

**Files:**
- Create: `src/data/collector.py`
- Create: `src/data/processor.py`
- Test: `tests/test_processor.py`

- [ ] **Step 1: 编写processor模块的测试**

`tests/test_processor.py`：

```python
import json
from src.data.processor import process_law_text, process_case_text


def test_process_law_text_splits_into_articles():
    raw_text = """
    中华人民共和国刑法
    第一编 总则
    第一章 刑法的任务、基本原则和适用范围
    第一条 为了惩罚犯罪，保护人民，根据宪法，制定本法。
    第二条 中华人民共和国刑法的任务，是用刑罚同一切犯罪行为作斗争。
    """
    result = process_law_text(raw_text, law_name="中华人民共和国刑法")
    assert len(result) >= 2
    assert result[0]["law_name"] == "中华人民共和国刑法"
    assert "第一条" in result[0]["article_number"]
    assert "为了惩罚犯罪" in result[0]["content"]


def test_process_case_text_extracts_fields():
    raw_case = {
        "case_id": "CASE001",
        "case_type": "刑事",
        "crime": "盗窃",
        "fact": "被告人张某于2023年1月盗窃他人财物",
        "judgment": "判处有期徒刑六个月",
    }
    result = process_case_text(raw_case)
    assert result["case_id"] == "CASE001"
    assert result["crime"] == "盗窃"
    assert result["judgment"] == "判处有期徒刑六个月"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_processor.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'src.data.processor'`

- [ ] **Step 3: 实现src/data/collector.py**

```python
"""数据采集模块：下载公开法律法规和案例数据集"""

import json
import urllib.request
from pathlib import Path

from src.config import get_project_root

RAW_DATA_DIR = get_project_root() / "data" / "raw"


def download_cail_dataset(save_path: Path | None = None) -> Path:
    """下载CAIL（中国法律人工智能挑战赛）数据集

    CAIL数据集包含刑法相关案例，来源为GitHub开源发布。
    如下载失败，请手动从 https://github.com/china-ai-law-challenge 下载。
    """
    if save_path is None:
        save_path = RAW_DATA_DIR / "cail_cases.json"

    save_path.parent.mkdir(parents=True, exist_ok=True)

    if save_path.exists():
        return save_path

    # CAIL 2018 数据集的示例URL（实际使用时替换为有效下载链接）
    url = "https://github.com/china-ai-law-challenge/CAIL2018/raw/master/data/data_train.json"

    try:
        urllib.request.urlretrieve(url, save_path)
    except Exception as e:
        print(f"下载失败: {e}")
        print(f"请手动下载数据集到 {save_path}")

    return save_path


def load_sample_laws() -> list[dict]:
    """加载内置的示例法律条文数据

    在没有完整数据集时，使用内置示例数据进行开发测试。
    """
    sample_data = [
        {
            "law_name": "中华人民共和国刑法",
            "chapter": "第二编 分则",
            "article_number": "第二百三十二条",
            "content": "故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑；情节较轻的，处三年以上十年以下有期徒刑。",
        },
        {
            "law_name": "中华人民共和国刑法",
            "chapter": "第二编 分则",
            "article_number": "第二百六十四条",
            "content": "盗窃公私财物，数额较大的，或者多次盗窃、入户盗窃、携带凶器盗窃、扒窃的，处三年以下有期徒刑、拘役或者管制，并处或者单处罚金；数额巨大或者有其他严重情节的，处三年以上十年以下有期徒刑，并处罚金；数额特别巨大或者有其他特别严重情节的，处十年以上有期徒刑或者无期徒刑，并处罚金或者没收财产。",
        },
        {
            "law_name": "中华人民共和国劳动合同法",
            "chapter": "第一章 总则",
            "article_number": "第十条",
            "content": "建立劳动关系，应当订立书面劳动合同。已建立劳动关系，未同时订立书面劳动合同的，应当自用工之日起一个月内订立书面劳动合同。",
        },
        {
            "law_name": "中华人民共和国劳动合同法",
            "chapter": "第七章 法律责任",
            "article_number": "第八十二条",
            "content": "用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。",
        },
        {
            "law_name": "中华人民共和国民法典",
            "chapter": "第一编 总则",
            "article_number": "第一百一十条",
            "content": "自然人享有生命权、身体权、健康权、姓名权、肖像权、名誉权、荣誉权、隐私权、婚姻自主权等权利。法人、非法人组织享有名称权、名誉权和荣誉权。",
        },
    ]
    return sample_data


def load_sample_cases() -> list[dict]:
    """加载内置的示例案例数据"""
    sample_data = [
        {
            "case_id": "CASE001",
            "case_type": "刑事",
            "crime": "故意杀人",
            "fact": "被告人李某因家庭纠纷持刀将被害人王某刺死",
            "judgment": "判处无期徒刑",
            "applicable_law": "刑法第二百三十二条",
        },
        {
            "case_id": "CASE002",
            "case_type": "刑事",
            "crime": "盗窃",
            "fact": "被告人张某多次入户盗窃，盗窃金额累计5万元",
            "judgment": "判处有期徒刑三年，并处罚金",
            "applicable_law": "刑法第二百六十四条",
        },
        {
            "case_id": "CASE003",
            "case_type": "劳动争议",
            "crime": "",
            "fact": "原告入职被告公司6个月，被告未签订书面劳动合同",
            "judgment": "被告支付双倍工资差额",
            "applicable_law": "劳动合同法第八十二条",
        },
    ]
    return sample_data


def save_data(data: list[dict], filename: str) -> Path:
    """保存数据到processed目录"""
    processed_dir = get_project_root() / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    save_path = processed_dir / filename
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return save_path
```

- [ ] **Step 4: 实现src/data/processor.py**

```python
"""数据处理模块：将原始数据结构化为统一JSON格式"""

import re


def process_law_text(raw_text: str, law_name: str = "") -> list[dict]:
    """将法规文本拆分为法-章-条三级结构

    Args:
        raw_text: 法规原始文本
        law_name: 法规名称

    Returns:
        结构化的法规条款列表，每项包含 law_name, chapter, article_number, content
    """
    articles = []
    current_chapter = ""

    # 匹配章标题
    chapter_pattern = re.compile(r"第[一二三四五六七八九十百]+章\s+.+")
    # 匹配条号
    article_pattern = re.compile(r"第[一二三四五六七八九十百零]+条")

    lines = raw_text.strip().split("\n")
    i = 0

    # 提取法名（如果未提供）
    if not law_name:
        for line in lines:
            if "中华人民共和国" in line and "法" in line:
                law_name = line.strip()
                break

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 检测章标题
        if chapter_pattern.match(line):
            current_chapter = line
            i += 1
            continue

        # 检测条款
        match = article_pattern.match(line)
        if match:
            article_number = match.group()
            # 条款内容可能跨行
            content = line[len(article_number):].strip()
            i += 1
            # 继续读取后续行直到下一个条或章
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                if article_pattern.match(next_line) or chapter_pattern.match(next_line):
                    break
                content += next_line
                i += 1

            articles.append({
                "law_name": law_name,
                "chapter": current_chapter,
                "article_number": article_number,
                "content": content,
            })
        else:
            i += 1

    return articles


def process_case_text(raw_case: dict) -> dict:
    """将案例数据处理为统一结构

    Args:
        raw_case: 原始案例数据字典

    Returns:
        结构化的案例数据，包含 case_id, case_type, crime, fact, judgment, applicable_law
    """
    return {
        "case_id": raw_case.get("case_id", ""),
        "case_type": raw_case.get("case_type", ""),
        "crime": raw_case.get("crime", ""),
        "fact": raw_case.get("fact", ""),
        "judgment": raw_case.get("judgment", ""),
        "applicable_law": raw_case.get("applicable_law", ""),
    }


def batch_process_cases(raw_cases: list[dict]) -> list[dict]:
    """批量处理案例数据"""
    return [process_case_text(case) for case in raw_cases]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
uv run pytest tests/test_processor.py -v
```

预期：PASS

- [ ] **Step 6: 提交**

```bash
git add src/data/ tests/test_processor.py
git commit -m "feat: add data collector and processor modules with tests"
```

---

## Task 3: 知识图谱构建

**Files:**
- Create: `src/data/kg_builder.py`
- Test: `tests/test_kg_builder.py`

前置条件：Neo4j Community Edition 已安装并运行。推荐Docker方式：

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5-community
```

- [ ] **Step 1: 编写kg_builder模块的测试**

`tests/test_kg_builder.py`：

```python
import pytest
from unittest.mock import MagicMock, patch

from src.data.kg_builder import build_cypher_for_law_node, build_cypher_for_case_node, build_cypher_for_relation


def test_build_cypher_for_law_node():
    law = {
        "law_name": "中华人民共和国刑法",
        "chapter": "第二编 分则",
        "article_number": "第二百三十二条",
        "content": "故意杀人的，处死刑...",
    }
    cypher, params = build_cypher_for_law_node(law)
    assert "CREATE" in cypher or "MERGE" in cypher
    assert params["law_name"] == "中华人民共和国刑法"
    assert params["article_number"] == "第二百三十二条"


def test_build_cypher_for_case_node():
    case = {
        "case_id": "CASE001",
        "case_type": "刑事",
        "crime": "故意杀人",
        "fact": "被告人李某持刀杀人",
        "judgment": "判处无期徒刑",
        "applicable_law": "刑法第二百三十二条",
    }
    cypher, params = build_cypher_for_case_node(case)
    assert "CREATE" in cypher or "MERGE" in cypher
    assert params["case_id"] == "CASE001"


def test_build_cypher_for_relation():
    cypher, params = build_cypher_for_relation(
        from_label="Case", from_id_field="case_id", from_id_value="CASE001",
        to_label="Law", to_id_field="article_number", to_id_value="第二百三十二条",
        relation_type="APPLIES",
    )
    assert "APPLIES" in cypher
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_kg_builder.py -v
```

预期：FAIL

- [ ] **Step 3: 实现src/data/kg_builder.py**

```python
"""知识图谱构建模块：提取实体关系并写入Neo4j"""

from src.config import load_config


def get_neo4j_driver():
    """获取Neo4j驱动"""
    from neo4j import GraphDatabase

    config = load_config()
    driver = GraphDatabase.driver(
        config["neo4j"]["uri"],
        auth=(config["neo4j"]["username"], config["neo4j"]["password"]),
    )
    return driver


def build_cypher_for_law_node(law: dict) -> tuple[str, dict]:
    """构建法规节点的Cypher语句和参数"""
    cypher = """
    MERGE (l:Law {article_number: $article_number, law_name: $law_name})
    SET l.chapter = $chapter, l.content = $content
    """
    params = {
        "law_name": law["law_name"],
        "chapter": law.get("chapter", ""),
        "article_number": law["article_number"],
        "content": law["content"],
    }
    return cypher, params


def build_cypher_for_case_node(case: dict) -> tuple[str, dict]:
    """构建案例节点的Cypher语句和参数"""
    cypher = """
    MERGE (c:Case {case_id: $case_id})
    SET c.case_type = $case_type, c.crime = $crime,
        c.fact = $fact, c.judgment = $judgment,
        c.applicable_law = $applicable_law
    """
    params = {
        "case_id": case["case_id"],
        "case_type": case.get("case_type", ""),
        "crime": case.get("crime", ""),
        "fact": case.get("fact", ""),
        "judgment": case.get("judgment", ""),
        "applicable_law": case.get("applicable_law", ""),
    }
    return cypher, params


def build_cypher_for_relation(
    from_label: str, from_id_field: str, from_id_value: str,
    to_label: str, to_id_field: str, to_id_value: str,
    relation_type: str,
) -> tuple[str, dict]:
    """构建关系边的Cypher语句和参数"""
    cypher = f"""
    MATCH (a:{from_label} {{{from_id_field}: $from_id}})
    MATCH (b:{to_label} {{{to_id_field}: $to_id}})
    MERGE (a)-[:{relation_type}]->(b)
    """
    params = {"from_id": from_id_value, "to_id": to_id_value}
    return cypher, params


def import_laws(laws: list[dict], driver=None) -> int:
    """批量导入法规节点到Neo4j

    Returns:
        成功导入的节点数量
    """
    if driver is None:
        driver = get_neo4j_driver()

    count = 0
    with driver.session() as session:
        for law in laws:
            cypher, params = build_cypher_for_law_node(law)
            session.run(cypher, params)
            count += 1
    return count


def import_cases(cases: list[dict], driver=None) -> int:
    """批量导入案例节点到Neo4j

    Returns:
        成功导入的节点数量
    """
    if driver is None:
        driver = get_neo4j_driver()

    count = 0
    with driver.session() as session:
        for case in cases:
            cypher, params = build_cypher_for_case_node(case)
            session.run(cypher, params)
            count += 1
    return count


def import_relations(cases: list[dict], driver=None) -> int:
    """根据案例的applicable_law字段建立案例-法规关系

    Returns:
        成功创建的关系数量
    """
    if driver is None:
        driver = get_neo4j_driver()

    count = 0
    with driver.session() as session:
        for case in cases:
            applicable_law = case.get("applicable_law", "")
            if not applicable_law:
                continue
            # 从applicable_law中提取条款号
            import re
            match = re.search(r"第[一二三四五六七八九十百零]+条", applicable_law)
            if match:
                article_number = match.group()
                cypher, params = build_cypher_for_relation(
                    from_label="Case", from_id_field="case_id",
                    from_id_value=case["case_id"],
                    to_label="Law", to_id_field="article_number",
                    to_id_value=article_number,
                    relation_type="APPLIES",
                )
                session.run(cypher, params)
                count += 1
    return count


def build_knowledge_graph(laws: list[dict], cases: list[dict]) -> dict:
    """构建完整知识图谱：导入节点+关系

    Returns:
        统计信息字典
    """
    driver = get_neo4j_driver()
    try:
        law_count = import_laws(laws, driver)
        case_count = import_cases(cases, driver)
        relation_count = import_relations(cases, driver)
        return {
            "law_nodes": law_count,
            "case_nodes": case_count,
            "relations": relation_count,
        }
    finally:
        driver.close()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_kg_builder.py -v
```

预期：PASS

- [ ] **Step 5: 运行导入脚本，将示例数据导入Neo4j**

创建临时脚本 `scripts/import_sample_data.py`：

```python
"""将示例数据导入Neo4j知识图谱"""
from src.data.collector import load_sample_laws, load_sample_cases
from src.data.kg_builder import build_knowledge_graph

laws = load_sample_laws()
cases = load_sample_cases()
stats = build_knowledge_graph(laws, cases)
print(f"导入完成: {stats}")
```

运行：

```bash
uv run python scripts/import_sample_data.py
```

预期输出类似：`导入完成: {'law_nodes': 5, 'case_nodes': 3, 'relations': 3}`

在Neo4j Browser (http://localhost:7474) 中验证：
```cypher
MATCH (n) RETURN n LIMIT 25
```

- [ ] **Step 6: 提交**

```bash
git add src/data/kg_builder.py tests/test_kg_builder.py
git commit -m "feat: add knowledge graph builder with Neo4j import"
```

---

## Task 4: 向量索引构建与检索

**Files:**
- Create: `src/retrieval/vector_search.py`
- Test: `tests/test_vector_search.py`

- [ ] **Step 1: 编写向量检索模块的测试**

`tests/test_vector_search.py`：

```python
from unittest.mock import patch, MagicMock

from src.retrieval.vector_search import build_documents, VectorSearchEngine


def test_build_documents_from_laws():
    laws = [
        {"law_name": "刑法", "article_number": "第二百三十二条", "content": "故意杀人的..."},
        {"law_name": "民法典", "article_number": "第一百一十条", "content": "自然人享有..."},
    ]
    docs = build_documents(laws, source_type="law")
    assert len(docs) == 2
    assert "故意杀人的" in docs[0].page_content
    assert docs[0].metadata["source_type"] == "law"


def test_vector_search_engine_build_and_query():
    laws = [
        {"law_name": "刑法", "article_number": "第二百三十二条", "content": "故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑"},
        {"law_name": "刑法", "article_number": "第二百六十四条", "content": "盗窃公私财物，数额较大的，处三年以下有期徒刑"},
        {"law_name": "劳动合同法", "article_number": "第八十二条", "content": "用人单位未与劳动者订立书面劳动合同的，应当支付双倍工资"},
    ]
    engine = VectorSearchEngine()
    docs = build_documents(laws, source_type="law")
    engine.build_index(docs)
    results = engine.query("盗窃罪怎么判", top_k=2)
    assert len(results) <= 2
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_vector_search.py -v
```

预期：FAIL

- [ ] **Step 3: 实现src/retrieval/vector_search.py**

```python
"""向量检索模块：FAISS索引构建和相似度查询"""

from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import load_config


def build_documents(items: list[dict], source_type: str = "law") -> list[Document]:
    """将结构化数据转为LangChain Document对象

    Args:
        items: 法规或案例的结构化数据列表
        source_type: "law" 或 "case"

    Returns:
        Document列表，page_content为可检索文本，metadata保留原始字段
    """
    docs = []
    for item in items:
        if source_type == "law":
            content = f"{item['law_name']} {item['article_number']}：{item['content']}"
            metadata = {
                "source_type": "law",
                "law_name": item["law_name"],
                "article_number": item["article_number"],
            }
        else:
            content = f"案例{item['case_id']}：{item['fact']} 判决：{item['judgment']}"
            metadata = {
                "source_type": "case",
                "case_id": item["case_id"],
                "crime": item.get("crime", ""),
            }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


class VectorSearchEngine:
    """向量检索引擎"""

    def __init__(self):
        config = load_config()
        self.embeddings = DashScopeEmbeddings(
            model=config["embedding"]["model"],
            dashscope_api_key=config["llm"]["api_key"],
        )
        self.vectorstore = None

    def build_index(self, documents: list[Document]) -> None:
        """构建FAISS索引"""
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

    def save_index(self, path: str) -> None:
        """保存索引到磁盘"""
        if self.vectorstore:
            self.vectorstore.save_local(path)

    def load_index(self, path: str) -> None:
        """从磁盘加载索引"""
        self.vectorstore = FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True,
        )

    def query(self, query_text: str, top_k: int = 5) -> list[Document]:
        """相似度检索

        Args:
            query_text: 查询文本
            top_k: 返回最相似的K个文档

        Returns:
            相似文档列表
        """
        if not self.vectorstore:
            raise ValueError("索引未构建，请先调用build_index或load_index")
        results = self.vectorstore.similarity_search(query_text, k=top_k)
        return results
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_vector_search.py -v
```

预期：PASS

- [ ] **Step 5: 提交**

```bash
git add src/retrieval/vector_search.py tests/test_vector_search.py
git commit -m "feat: add vector search engine with FAISS indexing"
```

---

## Task 5: 图检索与结果融合

**Files:**
- Create: `src/retrieval/graph_search.py`
- Create: `src/retrieval/fusion.py`
- Test: `tests/test_graph_search.py`
- Test: `tests/test_fusion.py`

- [ ] **Step 1: 编写图检索测试**

`tests/test_graph_search.py`：

```python
from src.retrieval.graph_search import extract_entities, build_graph_query


def test_extract_entities_finds_article_numbers():
    entities = extract_entities("刑法第232条怎么规定的？")
    assert any("第二百三十二条" in e or "232" in e for e in entities.get("article_numbers", []))


def test_extract_entities_finds_crimes():
    entities = extract_entities("盗窃罪和诈骗罪有什么区别？")
    assert "盗窃" in entities.get("crimes", []) or "盗窃罪" in entities.get("crimes", [])


def test_build_graph_query():
    entities = {
        "article_numbers": ["第二百三十二条"],
        "crimes": ["故意杀人"],
    }
    cypher = build_graph_query(entities, hop=2)
    assert "MATCH" in cypher
    assert "二百三十二" in cypher or "RETURN" in cypher
```

- [ ] **Step 2: 编写融合模块测试**

`tests/test_fusion.py`：

```python
from langchain_core.documents import Document
from src.retrieval.fusion import fuse_results


def test_fuse_results_deduplicates():
    doc1 = Document(page_content="内容1", metadata={"article_number": "第232条", "source_type": "law"})
    doc2 = Document(page_content="内容1（重复）", metadata={"article_number": "第232条", "source_type": "law"})

    vector_results = [doc1]
    graph_results = [doc2]

    fused = fuse_results(vector_results, graph_results, top_k=5)
    # 同一条款应去重
    article_numbers = [d.metadata.get("article_number") for d in fused]
    assert article_numbers.count("第232条") <= 1


def test_fuse_results_respects_top_k():
    docs = [
        Document(page_content=f"内容{i}", metadata={"source_type": "law"})
        for i in range(10)
    ]
    fused = fuse_results(docs[:5], docs[5:], top_k=3)
    assert len(fused) <= 3
```

- [ ] **Step 3: 运行测试确认失败**

```bash
uv run pytest tests/test_graph_search.py tests/test_fusion.py -v
```

预期：FAIL

- [ ] **Step 4: 实现src/retrieval/graph_search.py**

```python
"""图检索模块：Neo4j Cypher查询和实体抽取"""

import re

from openai import OpenAI

from src.config import load_config
from src.data.kg_builder import get_neo4j_driver


def extract_entities(question: str) -> dict:
    """从用户问题中提取法律实体

    Args:
        question: 用户自然语言问题

    Returns:
        包含 article_numbers, crimes, legal_terms 的字典
    """
    config = load_config()
    client = OpenAI(
        api_key=config["llm"]["api_key"],
        base_url=config["llm"]["base_url"],
    )

    prompt = f"""从以下法律问题中提取关键实体，返回JSON格式：
{{
  "article_numbers": ["提取到的条款号，如第二百三十二条"],
  "crimes": ["提取到的罪名，如盗窃"],
  "legal_terms": ["提取到的法律术语，如正当防卫"]
}}

问题：{question}

只返回JSON，不要其他内容。"""

    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    import json
    try:
        content = response.choices[0].message.content
        # 处理可能的markdown代码块包裹
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*", "", content)
        return json.loads(content)
    except (json.JSONDecodeError, KeyError):
        return {"article_numbers": [], "crimes": [], "legal_terms": []}


def build_graph_query(entities: dict, hop: int = 2) -> str:
    """根据提取的实体构建Cypher查询

    Args:
        entities: extract_entities返回的实体字典
        hop: 关系遍历跳数

    Returns:
        Cypher查询字符串
    """
    conditions = []

    article_numbers = entities.get("article_numbers", [])
    crimes = entities.get("crimes", [])
    legal_terms = entities.get("legal_terms", [])

    if article_numbers:
        nums = ", ".join([f'"{n}"' for n in article_numbers])
        conditions.append(f"l.article_number IN [{nums}]")

    if crimes:
        crime_conditions = " OR ".join([f'c.crime CONTAINS "{crime}"' for crime in crimes])
        conditions.append(crime_conditions)

    if not conditions:
        # 无明确实体时，返回空查询
        return "MATCH (n) RETURN n LIMIT 0"

    # 构建多跳查询
    match_clause = "MATCH (l:Law)"
    where_clause = f"WHERE {' OR '.join(conditions)}"
    return_clause = "RETURN l"

    if hop >= 1:
        # 一跳：找到关联案例
        query = f"""
        {match_clause}
        {where_clause}
        OPTIONAL MATCH (l)-[r1]-(c:Case)
        RETURN l, r1, c
        """
    else:
        query = f"{match_clause} {where_clause} {return_clause}"

    if hop >= 2:
        # 二跳：找到案例关联的其他法规
        query = f"""
        MATCH (l:Law)
        {where_clause}
        OPTIONAL MATCH (l)-[r1]-(c:Case)
        OPTIONAL MATCH (c)-[r2]-(l2:Law)
        RETURN l, r1, c, r2, l2
        """

    return query


def graph_search(question: str, top_k: int = 5) -> list[dict]:
    """执行图检索

    Args:
        question: 用户问题
        top_k: 返回结果数量上限

    Returns:
        检索到的法规和案例节点列表
    """
    entities = extract_entities(question)
    cypher = build_graph_query(entities)

    config = load_config()
    driver = get_neo4j_driver()
    results = []

    try:
        with driver.session() as session:
            records = session.run(cypher)
            seen = set()

            for record in records:
                for key in record.keys():
                    node = record[key]
                    # 跳过关系和非节点值
                    if not hasattr(node, "labels"):
                        continue
                    node_id = dict(node)
                    # 简单去重
                    identifier = str(node_id)
                    if identifier in seen:
                        continue
                    seen.add(identifier)

                    node_type = list(node.labels)[0] if node.labels else "Unknown"

                    results.append({
                        "type": node_type,
                        "properties": dict(node),
                    })

                    if len(results) >= top_k:
                        return results
    finally:
        driver.close()

    return results
```

- [ ] **Step 5: 实现src/retrieval/fusion.py**

```python
"""结果融合模块：向量+图双路检索结果合并排序"""

from langchain_core.documents import Document

from src.config import load_config
from src.retrieval.vector_search import VectorSearchEngine
from src.retrieval.graph_search import graph_search


def fuse_results(
    vector_results: list[Document],
    graph_results: list[dict],
    top_k: int = 8,
) -> list[Document]:
    """融合向量和图检索结果，去重后按权重排序

    Args:
        vector_results: 向量检索返回的Document列表
        graph_results: 图检索返回的节点字典列表
        top_k: 最终返回的结果数量

    Returns:
        融合后的Document列表
    """
    config = load_config()
    weights = config["retrieval"]["fusion_weights"]
    vector_weight = weights["vector"]
    graph_weight = weights["graph"]

    scored_docs = []

    for i, doc in enumerate(vector_results):
        score = vector_weight * (1.0 / (i + 1))  # 排名越高分越高
        scored_docs.append((score, doc))

    for i, node in enumerate(graph_results):
        properties = node.get("properties", {})
        node_type = node.get("type", "")

        if node_type == "Law":
            content = f"{properties.get('law_name', '')} {properties.get('article_number', '')}：{properties.get('content', '')}"
            metadata = {
                "source_type": "law",
                "law_name": properties.get("law_name", ""),
                "article_number": properties.get("article_number", ""),
            }
        elif node_type == "Case":
            content = f"案例{properties.get('case_id', '')}：{properties.get('fact', '')} 判决：{properties.get('judgment', '')}"
            metadata = {
                "source_type": "case",
                "case_id": properties.get("case_id", ""),
                "crime": properties.get("crime", ""),
            }
        else:
            continue

        doc = Document(page_content=content, metadata=metadata)
        score = graph_weight * (1.0 / (i + 1))

        # 检查是否与已有结果重复
        is_duplicate = False
        for existing_score, existing_doc in scored_docs:
            if _is_duplicate(doc, existing_doc):
                # 保留分数更高的
                existing_idx = scored_docs.index((existing_score, existing_doc))
                combined_score = existing_score + score
                scored_docs[existing_idx] = (combined_score, existing_doc)
                is_duplicate = True
                break

        if not is_duplicate:
            scored_docs.append((score, doc))

    # 按分数降序排列
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored_docs[:top_k]]


def _is_duplicate(doc1: Document, doc2: Document) -> bool:
    """判断两个文档是否重复"""
    meta1 = doc1.metadata
    meta2 = doc2.metadata

    # 同类型同ID视为重复
    if meta1.get("source_type") == meta2.get("source_type") == "law":
        return (meta1.get("article_number") == meta2.get("article_number")
                and meta1.get("law_name") == meta2.get("law_name"))

    if meta1.get("source_type") == meta2.get("source_type") == "case":
        return meta1.get("case_id") == meta2.get("case_id")

    return False


def hybrid_search(question: str, top_k: int = 8) -> list[Document]:
    """双路检索+融合的完整流程

    Args:
        question: 用户问题
        top_k: 最终返回结果数量

    Returns:
        融合后的Document列表
    """
    config = load_config()

    # 向量检索
    vector_engine = VectorSearchEngine()
    emb_path = str((config.get("embedding_save_path", "data/embeddings")))
    try:
        vector_engine.load_index(emb_path)
    except Exception:
        # 索引不存在时，从处理后的数据构建
        from src.data.collector import load_sample_laws, load_sample_cases
        from src.retrieval.vector_search import build_documents

        laws = load_sample_laws()
        cases = load_sample_cases()
        docs = build_documents(laws, source_type="law") + build_documents(cases, source_type="case")
        vector_engine.build_index(docs)
        vector_engine.save_index(emb_path)

    vector_top_k = config["retrieval"]["vector_top_k"]
    vector_results = vector_engine.query(question, top_k=vector_top_k)

    # 图检索
    graph_results = graph_search(question, top_k=top_k)

    # 融合
    return fuse_results(vector_results, graph_results, top_k=top_k)
```

- [ ] **Step 6: 运行测试确认通过**

```bash
uv run pytest tests/test_graph_search.py tests/test_fusion.py -v
```

预期：PASS

- [ ] **Step 7: 提交**

```bash
git add src/retrieval/ tests/test_graph_search.py tests/test_fusion.py
git commit -m "feat: add graph search and hybrid fusion retrieval"
```

---

## Task 6: 基础RAG问答与Streamlit界面

**Files:**
- Create: `src/retrieval/rag.py`
- Create: `src/app/main.py`

- [ ] **Step 1: 实现src/retrieval/rag.py**

```python
"""RAG核心模块：串联检索与LLM生成"""

from openai import OpenAI

from src.config import load_config
from src.retrieval.fusion import hybrid_search


def build_rag_prompt(question: str, context_docs: list) -> str:
    """构建RAG prompt

    Args:
        question: 用户问题
        context_docs: 检索到的上下文文档

    Returns:
        完整的prompt字符串
    """
    context_text = "\n\n".join(
        f"[{i+1}] {doc.page_content}"
        for i, doc in enumerate(context_docs)
    )

    prompt = f"""你是一个专业的法律咨询助手。请根据以下法律条文和案例资料回答用户的问题。

要求：
1. 回答必须引用具体的法条来源
2. 如果引用了案例，说明案例的参考价值
3. 如果检索资料不足以回答问题，请如实说明
4. 回答末尾标注"仅供参考，不构成法律意见"

参考资料：
{context_text}

用户问题：{question}

请给出专业、准确的法律分析："""

    return prompt


def rag_query(question: str) -> dict:
    """RAG问答完整流程

    Args:
        question: 用户问题

    Returns:
        包含 answer, sources 的字典
    """
    config = load_config()

    # 1. 检索
    context_docs = hybrid_search(question)

    # 2. 构建prompt
    prompt = build_rag_prompt(question, context_docs)

    # 3. 调用LLM生成回答
    client = OpenAI(
        api_key=config["llm"]["api_key"],
        base_url=config["llm"]["base_url"],
    )

    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=config["llm"]["temperature"],
        max_tokens=config["llm"]["max_tokens"],
    )

    answer = response.choices[0].message.content

    # 4. 整理引用来源
    sources = []
    for doc in context_docs:
        meta = doc.metadata
        if meta.get("source_type") == "law":
            sources.append(f"{meta.get('law_name', '')} {meta.get('article_number', '')}")
        elif meta.get("source_type") == "case":
            sources.append(f"案例 {meta.get('case_id', '')} ({meta.get('crime', '')})")

    return {
        "answer": answer,
        "sources": sources,
        "context_docs": context_docs,
    }
```

- [ ] **Step 2: 实现src/app/main.py**

```python
"""Streamlit入口：仅做展示，逻辑全部在模块中"""

import streamlit as st

from src.retrieval.rag import rag_query


def main():
    st.set_page_config(page_title="Lexiora 法律咨询助手", page_icon="⚖️", layout="wide")
    st.title("⚖️ Lexiora 法律咨询助手")
    st.caption("基于多Agent和GraphRAG的智能法律咨询系统")

    # 对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 展示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 用户输入
    if prompt := st.chat_input("请输入您的法律问题..."):
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用RAG（逻辑层，与UI分离）
        with st.chat_message("assistant"):
            with st.spinner("正在检索法律资料并分析..."):
                result = rag_query(prompt)

            st.markdown(result["answer"])

            # 展示引用来源
            if result["sources"]:
                with st.expander("📋 查看引用依据"):
                    for source in result["sources"]:
                        st.markdown(f"- {source}")

        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 测试Streamlit运行**

```bash
uv run streamlit run src/app/main.py
```

**里程碑验证**：在浏览器中输入"刑法第232条是什么"，系统返回法条内容和相关案例（使用示例数据）。

- [ ] **Step 4: 提交**

```bash
git add src/retrieval/rag.py src/app/main.py
git commit -m "feat: add RAG pipeline and Streamlit interface for phase 1 milestone"
```

---

## Task 7: Agent基础设施（LangGraph）

**Files:**
- Modify: `src/agents/__init__.py`
- Create: `src/agents/coordinator.py`

- [ ] **Step 1: 实现src/agents/coordinator.py**

```python
"""协调Agent：意图识别和领域路由"""

from openai import OpenAI

from src.config import load_config

DOMAINS = ["civil_law", "criminal_law", "labor_law", "admin_law", "general"]

DOMAIN_MAP = {
    "民法": "civil_law",
    "民事": "civil_law",
    "合同": "civil_law",
    "婚姻": "civil_law",
    "继承": "civil_law",
    "侵权": "civil_law",
    "刑法": "criminal_law",
    "刑事": "criminal_law",
    "犯罪": "criminal_law",
    "量刑": "criminal_law",
    "盗窃": "criminal_law",
    "杀人": "criminal_law",
    "劳动": "labor_law",
    "劳动合同": "labor_law",
    "工资": "labor_law",
    "社保": "labor_law",
    "工伤": "labor_law",
    "行政": "admin_law",
    "行政处罚": "admin_law",
    "行政诉讼": "admin_law",
}


def identify_domain(question: str) -> dict:
    """识别用户问题所属的法律领域和意图

    Args:
        question: 用户自然语言问题

    Returns:
        包含 domain, intent, keywords 的字典
    """
    config = load_config()
    client = OpenAI(
        api_key=config["llm"]["api_key"],
        base_url=config["llm"]["base_url"],
    )

    prompt = f"""分析以下法律问题，返回JSON格式：
{{
  "domain": "民事/刑事/劳动/行政/通用 中的一个",
  "intent": "法条查询/案例分析/法律建议/概念解释 中的一个",
  "keywords": ["提取的关键词列表"]
}}

问题：{question}

只返回JSON，不要其他内容。"""

    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    import json
    import re
    try:
        content = response.choices[0].message.content
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*", "", content)
        result = json.loads(content)
        # 将中文领域映射到内部标识
        domain_zh = result.get("domain", "通用")
        domain_en = "general"
        for zh_key, en_val in DOMAIN_MAP.items():
            if zh_key in domain_zh:
                domain_en = en_val
                break
        result["domain"] = domain_en
        result["domain_zh"] = domain_zh
        return result
    except (json.JSONDecodeError, KeyError):
        return {
            "domain": "general",
            "domain_zh": "通用",
            "intent": "法律建议",
            "keywords": [],
        }
```

- [ ] **Step 2: 编写测试**

`tests/test_coordinator.py`：

```python
from src.agents.coordinator import identify_domain, DOMAIN_MAP


def test_domain_map_covers_all_internal_domains():
    """DOMAIN_MAP应覆盖所有定义的领域"""
    mapped_values = set(DOMAIN_MAP.values())
    for domain in ["civil_law", "criminal_law", "labor_law", "admin_law"]:
        assert domain in mapped_values
```

- [ ] **Step 3: 运行测试确认通过**

```bash
uv run pytest tests/test_coordinator.py -v
```

- [ ] **Step 4: 提交**

```bash
git add src/agents/coordinator.py tests/test_coordinator.py
git commit -m "feat: add coordinator agent with domain identification"
```

---

## Task 8: 专业Agent基类

**Files:**
- Create: `src/agents/domain_agent.py`
- Create: `src/agents/config/criminal_law.yaml`
- Create: `src/agents/config/civil_law.yaml`
- Create: `src/agents/config/labor_law.yaml`
- Create: `src/agents/config/admin_law.yaml`
- Create: `src/agents/config/general.yaml`

- [ ] **Step 1: 创建各领域prompt配置**

`src/agents/config/criminal_law.yaml`：

```yaml
domain: "criminal_law"
domain_zh: "刑法"
system_prompt: |
  你是一位专业的刑法咨询专家。你精通中华人民共和国刑法及相关司法解释。

  回答要求：
  1. 明确引用刑法条款编号和内容
  2. 区分罪与非罪的界限
  3. 说明量刑幅度和从轻/从重情节
  4. 如有相关案例，说明参考价值
  5. 回答末尾标注"以上分析仅供参考，不构成法律意见。具体案件请咨询专业律师。"
```

`src/agents/config/labor_law.yaml`：

```yaml
domain: "labor_law"
domain_zh: "劳动法"
system_prompt: |
  你是一位专业的劳动法咨询专家。你精通劳动合同法、劳动法、社会保险法及相关法规。

  回答要求：
  1. 明确引用法律条款编号和内容
  2. 区分劳动者和用人单位的权利义务
  3. 说明维权途径和时效
  4. 如有相关案例，说明参考价值
  5. 回答末尾标注"以上分析仅供参考，不构成法律意见。具体案件请咨询专业律师。"
```

`src/agents/config/civil_law.yaml`：

```yaml
domain: "civil_law"
domain_zh: "民法"
system_prompt: |
  你是一位专业的民法咨询专家。你精通民法典及相关民事法律。

  回答要求：
  1. 明确引用民法典条款编号和内容
  2. 区分各类民事法律关系
  3. 说明权利救济途径
  4. 如有相关案例，说明参考价值
  5. 回答末尾标注"以上分析仅供参考，不构成法律意见。具体案件请咨询专业律师。"
```

`src/agents/config/admin_law.yaml`：

```yaml
domain: "admin_law"
domain_zh: "行政法"
system_prompt: |
  你是一位专业的行政法咨询专家。你精通行政处罚法、行政诉讼法及相关法规。

  回答要求：
  1. 明确引用法律条款编号和内容
  2. 区分行政行为的合法性
  3. 说明行政复议和行政诉讼的途径
  4. 如有相关案例，说明参考价值
  5. 回答末尾标注"以上分析仅供参考，不构成法律意见。具体案件请咨询专业律师。"
```

`src/agents/config/general.yaml`：

```yaml
domain: "general"
domain_zh: "通用"
system_prompt: |
  你是一位专业的法律咨询助手，能够解答各类基础法律问题。

  回答要求：
  1. 尽量引用具体的法律条款
  2. 明确说明问题涉及的法律领域
  3. 如问题超出你的专业知识范围，请如实说明并建议咨询专业律师
  4. 回答末尾标注"以上分析仅供参考，不构成法律意见。具体案件请咨询专业律师。"
```

- [ ] **Step 2: 实现src/agents/domain_agent.py**

```python
"""专业Agent基类：可复用的领域问答Agent"""

from pathlib import Path

import yaml
from openai import OpenAI

from src.config import load_config, get_project_root
from src.retrieval.fusion import hybrid_search


class DomainAgent:
    """领域专业Agent

    根据领域配置加载对应的系统prompt，调用GraphRAG检索并生成回答。
    """

    def __init__(self, domain: str):
        self.domain = domain
        self.config_data = self._load_domain_config(domain)
        self.system_prompt = self.config_data["system_prompt"]

    def _load_domain_config(self, domain: str) -> dict:
        """加载领域配置文件"""
        config_path = get_project_root() / "src" / "agents" / "config" / f"{domain}.yaml"
        if not config_path.exists():
            # 回退到通用配置
            config_path = get_project_root() / "src" / "agents" / "config" / "general.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def answer(self, question: str, intent: str = "", keywords: list[str] | None = None) -> dict:
        """生成领域专业回答

        Args:
            question: 用户问题
            intent: 意图标签
            keywords: 关键词列表

        Returns:
            包含 answer, sources 的字典
        """
        config = load_config()

        # 1. 检索相关知识
        context_docs = hybrid_search(question)

        # 2. 构建上下文
        context_text = "\n\n".join(
            f"[{i+1}] {doc.page_content}"
            for i, doc in enumerate(context_docs)
        )

        # 3. 调用LLM
        client = OpenAI(
            api_key=config["llm"]["api_key"],
            base_url=config["llm"]["base_url"],
        )

        user_message = f"""参考资料：
{context_text}

用户问题：{question}
问题意图：{intent}
关键词：{', '.join(keywords or [])}

请根据参考资料和专业判断给出回答。"""

        response = client.chat.completions.create(
            model=config["llm"]["model"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=config["llm"]["temperature"],
            max_tokens=config["llm"]["max_tokens"],
        )

        answer = response.choices[0].message.content

        # 4. 整理来源
        sources = []
        for doc in context_docs:
            meta = doc.metadata
            if meta.get("source_type") == "law":
                sources.append(f"{meta.get('law_name', '')} {meta.get('article_number', '')}")
            elif meta.get("source_type") == "case":
                sources.append(f"案例 {meta.get('case_id', '')} ({meta.get('crime', '')})")

        return {
            "answer": answer,
            "sources": sources,
            "domain": self.domain,
            "context_docs": context_docs,
        }
```

- [ ] **Step 3: 编写测试**

`tests/test_domain_agent.py`：

```python
from src.agents.domain_agent import DomainAgent


def test_domain_agent_loads_criminal_law_config():
    agent = DomainAgent("criminal_law")
    assert agent.domain == "criminal_law"
    assert "刑法" in agent.system_prompt


def test_domain_agent_falls_back_to_general():
    agent = DomainAgent("nonexistent_domain")
    assert agent.domain == "nonexistent_domain"
    assert "法律咨询" in agent.system_prompt
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_domain_agent.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/agents/domain_agent.py src/agents/config/ tests/test_domain_agent.py
git commit -m "feat: add domain agent base class with per-domain prompt configs"
```

---

## Task 9: 多Agent编排（LangGraph）

**Files:**
- Modify: `src/agents/coordinator.py` — 添加LangGraph图定义
- Modify: `src/app/main.py` — 更新为使用Agent流程

- [ ] **Step 1: 在coordinator.py中添加LangGraph图定义**

在 `src/agents/coordinator.py` 底部追加：

```python
from langgraph.graph import StateGraph, END
from src.agents.domain_agent import DomainAgent
from typing import TypedDict, Annotated


class AgentState(TypedDict):
    """Agent工作流状态"""
    question: str
    domain: str
    domain_zh: str
    intent: str
    keywords: list[str]
    answer: str
    sources: list[str]
    context_docs: list


def route_by_domain(state: AgentState) -> str:
    """根据领域路由到对应Agent节点"""
    return state["domain"]


def identify_intent_node(state: AgentState) -> dict:
    """意图识别节点"""
    result = identify_domain(state["question"])
    return {
        "domain": result["domain"],
        "domain_zh": result["domain_zh"],
        "intent": result["intent"],
        "keywords": result["keywords"],
    }


def create_domain_node(domain: str):
    """创建领域Agent节点函数"""
    def domain_node(state: AgentState) -> dict:
        agent = DomainAgent(domain)
        result = agent.answer(
            question=state["question"],
            intent=state["intent"],
            keywords=state["keywords"],
        )
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "context_docs": result["context_docs"],
        }
    return domain_node


def build_agent_graph() -> StateGraph:
    """构建多Agent工作流图"""
    workflow = StateGraph(AgentState)

    # 添加意图识别节点
    workflow.add_node("identify_intent", identify_intent_node)

    # 添加各领域Agent节点
    for domain in DOMAINS:
        workflow.add_node(domain, create_domain_node(domain))

    # 设置入口
    workflow.set_entry_point("identify_intent")

    # 添加条件路由：从意图识别到对应领域Agent
    workflow.add_conditional_edges(
        "identify_intent",
        route_by_domain,
        {domain: domain for domain in DOMAINS},
    )

    # 所有领域Agent指向结束
    for domain in DOMAINS:
        workflow.add_edge(domain, END)

    return workflow.compile()


def ask_agent(question: str) -> dict:
    """多Agent问答入口函数

    Args:
        question: 用户问题

    Returns:
        包含 answer, sources, domain 的字典
    """
    graph = build_agent_graph()
    result = graph.invoke({
        "question": question,
        "domain": "",
        "domain_zh": "",
        "intent": "",
        "keywords": [],
        "answer": "",
        "sources": [],
        "context_docs": [],
    })
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "domain": result["domain"],
        "domain_zh": result["domain_zh"],
    }
```

- [ ] **Step 2: 更新src/app/main.py使用Agent流程**

```python
"""Streamlit入口：仅做展示，逻辑全部在模块中"""

import streamlit as st

from src.agents.coordinator import ask_agent


def main():
    st.set_page_config(page_title="Lexiora 法律咨询助手", page_icon="⚖️", layout="wide")
    st.title("⚖️ Lexiora 法律咨询助手")
    st.caption("基于多Agent和GraphRAG的智能法律咨询系统")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📋 查看引用依据"):
                    for source in msg["sources"]:
                        st.markdown(f"- {source}")

    if prompt := st.chat_input("请输入您的法律问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在分析问题并检索法律资料..."):
                result = ask_agent(prompt)

            # 显示领域标签
            st.caption(f"📂 识别领域：{result.get('domain_zh', '通用')}")
            st.markdown(result["answer"])

            if result["sources"]:
                with st.expander("📋 查看引用依据"):
                    for source in result["sources"]:
                        st.markdown(f"- {source}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 测试完整流程**

```bash
uv run streamlit run src/app/main.py
```

**里程碑验证**：输入"劳动仲裁的时效是多久"，系统正确识别劳动法领域并给出专业回答。

- [ ] **Step 4: 提交**

```bash
git add src/agents/coordinator.py src/app/main.py
git commit -m "feat: add multi-agent orchestration with LangGraph and update UI"
```

---

## Task 10: 审查Agent

**Files:**
- Create: `src/agents/reviewer.py`
- Test: `tests/test_reviewer.py`

- [ ] **Step 1: 编写审查Agent测试**

`tests/test_reviewer.py`：

```python
from src.agents.reviewer import review_answer


def test_review_answer_passes_with_citations():
    answer = "根据刑法第232条，故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑。"
    sources = ["中华人民共和国刑法 第二百三十二条"]
    context_docs = []
    result = review_answer(answer, sources, context_docs)
    assert result["passed"] is True


def test_review_answer_fails_without_citations():
    answer = "故意杀人罪会被判处很重的刑罚。"
    sources = []
    context_docs = []
    result = review_answer(answer, sources, context_docs)
    assert result["passed"] is False
    assert "引用" in result["reason"] or "法条" in result["reason"]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_reviewer.py -v
```

- [ ] **Step 3: 实现src/agents/reviewer.py**

```python
"""审查Agent：对生成回答进行质量校验"""

import re

from openai import OpenAI

from src.config import load_config


def check_has_citation(answer: str) -> bool:
    """检查回答是否包含法条引用"""
    patterns = [
        r"第[一二三四五六七八九十百零]+条",
        r"第\d+条",
        r"《.+?》",
    ]
    return any(re.search(pattern, answer) for pattern in patterns)


def check_citation_accuracy(answer: str, sources: list[str]) -> dict:
    """检查引用是否与检索来源一致

    Returns:
        包含 accurate(bool), unmatched(list) 的字典
    """
    # 提取回答中提及的条款号
    cited_articles = re.findall(r"第[一二三四五六七八九十百零]+条", answer)
    if not cited_articles:
        return {"accurate": True, "unmatched": []}

    # 检查是否在来源中
    unmatched = []
    source_text = " ".join(sources)
    for article in cited_articles:
        if article not in source_text:
            unmatched.append(article)

    return {
        "accurate": len(unmatched) == 0,
        "unmatched": unmatched,
    }


def review_answer(
    answer: str,
    sources: list[str],
    context_docs: list | None = None,
) -> dict:
    """审查Agent：校验回答质量

    Args:
        answer: 生成的回答文本
        sources: 引用来源列表
        context_docs: 检索到的上下文文档

    Returns:
        包含 passed, reason, score 的字典
    """
    issues = []

    # 检查1：是否有法条引用
    if not check_has_citation(answer):
        issues.append("回答未包含任何法条引用")
        if not sources:
            issues.append("无检索来源支持")

    # 检查2：引用准确性
    citation_check = check_citation_accuracy(answer, sources)
    if not citation_check["accurate"]:
        unmatched_str = "、".join(citation_check["unmatched"])
        issues.append(f"以下引用未在检索结果中找到：{unmatched_str}，可能存在幻觉")

    # 检查3：免责声明
    if "仅供参考" not in answer and "不构成法律意见" not in answer:
        issues.append("缺少免责声明")

    if issues:
        return {
            "passed": False,
            "reason": "；".join(issues),
            "score": max(0, 1.0 - 0.3 * len(issues)),
        }
    else:
        return {
            "passed": True,
            "reason": "审查通过",
            "score": 1.0,
        }
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_reviewer.py -v
```

- [ ] **Step 5: 将审查Agent集成到LangGraph流程中**

在 `src/agents/coordinator.py` 的 `build_agent_graph` 函数中，添加审查节点：

```python
from src.agents.reviewer import review_answer

def review_node(state: AgentState) -> dict:
    """审查节点：校验回答质量"""
    review_result = review_answer(
        answer=state["answer"],
        sources=state["sources"],
        context_docs=state.get("context_docs", []),
    )
    return {"review_passed": review_result["passed"], "review_reason": review_result["reason"]}
```

在图中添加审查节点和条件边（审查通过→END，审查不通过→重新路由到领域Agent），最多重试1次。

- [ ] **Step 6: 提交**

```bash
git add src/agents/reviewer.py src/agents/coordinator.py tests/test_reviewer.py
git commit -m "feat: add reviewer agent with citation and accuracy checks"
```

---

## Task 11: 多轮对话支持

**Files:**
- Modify: `src/agents/coordinator.py` — 添加对话历史处理
- Modify: `src/app/main.py` — 使用st.chat_message展示对话历史

- [ ] **Step 1: 在AgentState中添加history字段**

```python
class AgentState(TypedDict):
    question: str
    history: list[dict]  # 新增：对话历史
    domain: str
    domain_zh: str
    intent: str
    keywords: list[str]
    answer: str
    sources: list[str]
    context_docs: list
    review_passed: bool
    review_reason: str
```

- [ ] **Step 2: 修改意图识别节点，结合历史上下文**

在 `identify_intent_node` 中，将最近的对话历史拼接到问题上下文里，帮助处理追问场景。

- [ ] **Step 3: 更新Streamlit界面，传入对话历史**

- [ ] **Step 4: 端到端测试追问场景**

输入"盗窃罪怎么判刑" → "如果是未成年呢"，验证系统能理解追问。

- [ ] **Step 5: 提交**

```bash
git add src/agents/coordinator.py src/app/main.py
git commit -m "feat: add multi-turn conversation support with context awareness"
```

---

## Task 12: UI完善与最终集成

**Files:**
- Modify: `src/app/main.py` — UI优化
- Create: `README.md`

- [ ] **Step 1: Streamlit UI优化**

- 侧边栏展示检索依据（法条引用、案例列表）
- 回答中法条引用可展开查看详情
- 响应式布局优化

- [ ] **Step 2: 编写README.md**

包含：项目说明、安装步骤、使用方法、架构图、技术栈说明。

- [ ] **Step 3: 端到端完整测试**

测试场景：
1. 民法问题："民法典关于名誉权怎么规定的？"
2. 刑法问题："盗窃罪的量刑标准是什么？"
3. 劳动法问题："公司不签劳动合同怎么办？"
4. 追问场景："如果是未成年呢？"
5. 无结果场景：输入与法律无关的问题

- [ ] **Step 4: 最终提交**

```bash
git add .
git commit -m "feat: finalize UI polish, README, and end-to-end integration"
```

---

## 依赖关系

```
Task 1 → Task 2 → Task 3（图）┐
                  Task 4（向量）┘ → Task 5 → Task 6
                                         ↓
                                       Task 7 → Task 8 → Task 9 → Task 10 → Task 11 → Task 12
```

Task 3 和 Task 4 可并行，但都依赖 Task 2。

---

## 风险与应对

| 风险 | 应对 |
|------|------|
| 通义千问API免费额度不足 | 开发用qwen-turbo（便宜），展示用qwen-plus |
| CAIL数据集下载失败 | 内置示例数据足够开发，后续手动补充 |
| Neo4j安装困难 | Docker一键部署，提供完整命令 |
| LLM幻觉问题 | 审查Agent自动检测，回答中标注"仅供参考" |
| LangGraph版本变动 | poetry.lock锁定版本，参考官方最新文档 |

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
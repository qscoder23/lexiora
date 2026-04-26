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
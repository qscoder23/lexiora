import os

import pytest
from src.retrieval.graph_search import extract_entities, build_graph_query


def test_build_graph_query():
    entities = {
        "article_numbers": ["第二百三十二条"],
        "crimes": ["故意杀人"],
    }
    cypher = build_graph_query(entities, hop=2)
    assert "MATCH" in cypher
    assert "二百三十二" in cypher or "RETURN" in cypher


@pytest.mark.skipif(not os.environ.get("DASHSCOPE_API_KEY"), reason="Requires DASHSCOPE_API_KEY")
def test_extract_entities_finds_article_numbers():
    entities = extract_entities("刑法第232条怎么规定的？")
    assert any("第二百三十二条" in e or "232" in e for e in entities.get("article_numbers", []))


@pytest.mark.skipif(not os.environ.get("DASHSCOPE_API_KEY"), reason="Requires DASHSCOPE_API_KEY")
def test_extract_entities_finds_crimes():
    entities = extract_entities("盗窃罪和诈骗罪有什么区别？")
    assert "盗窃" in entities.get("crimes", []) or "盗窃罪" in entities.get("crimes", [])
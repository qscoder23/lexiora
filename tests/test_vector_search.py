import os
from unittest.mock import patch, MagicMock

import pytest
from langchain_core.documents import Document

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


@pytest.mark.skipif(not os.environ.get("DASHSCOPE_API_KEY"), reason="Requires DASHSCOPE_API_KEY")
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
from langchain_core.documents import Document
from src.retrieval.fusion import fuse_results


def test_fuse_results_deduplicates():
    doc1 = Document(page_content="内容1", metadata={"article_number": "第232条", "source_type": "law", "law_name": "刑法"})

    vector_results = [doc1]
    graph_results = [
        {"type": "Law", "properties": {"article_number": "第232条", "law_name": "刑法", "content": "故意杀人的..."}}
    ]

    fused = fuse_results(vector_results, graph_results, top_k=5)
    # 同一条款应去重
    article_numbers = [d.metadata.get("article_number") for d in fused]
    assert article_numbers.count("第232条") <= 1


def test_fuse_results_respects_top_k():
    docs = [
        Document(page_content=f"内容{i}", metadata={"source_type": "law", "article_number": f"第{i}条", "law_name": "法"})
        for i in range(10)
    ]
    graph_results = [
        {"type": "Law", "properties": {"article_number": f"第{i}条", "law_name": "法", "content": f"内容{i}"}}
        for i in range(10)
    ]
    fused = fuse_results(docs[:5], graph_results[:5], top_k=3)
    assert len(fused) <= 3
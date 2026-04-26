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
        return meta1.get("article_number") == meta2.get("article_number") and meta1.get(
            "law_name"
        ) == meta2.get("law_name")

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
        docs = build_documents(laws, source_type="law") + build_documents(
            cases, source_type="case"
        )
        vector_engine.build_index(docs)
        vector_engine.save_index(emb_path)

    vector_top_k = config["retrieval"]["vector_top_k"]
    vector_results = vector_engine.query(question, top_k=vector_top_k)

    # 图检索
    graph_results = graph_search(question, top_k=top_k)

    # 融合
    return fuse_results(vector_results, graph_results, top_k=top_k)

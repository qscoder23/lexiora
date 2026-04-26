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
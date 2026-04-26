"""审查Agent：对生成回答进行质量校验"""

import re


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
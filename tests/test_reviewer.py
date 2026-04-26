from src.agents.reviewer import review_answer


def test_review_answer_passes_with_citations():
    answer = "根据刑法第二百三十二条，故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑。以上分析仅供参考，不构成法律意见。"
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
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
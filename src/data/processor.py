"""数据处理模块：将原始数据结构化为统一JSON格式"""

import re


def process_law_text(raw_text: str, law_name: str = "") -> list[dict]:
    """将法规文本拆分为法-章-条三级结构

    Args:
        raw_text: 法规原始文本
        law_name: 法规名称

    Returns:
        结构化的法规条款列表，每项包含 law_name, chapter, article_number, content
    """
    articles = []
    current_chapter = ""

    # 匹配章标题
    chapter_pattern = re.compile(r"第[一二三四五六七八九十百]+章\s+.+")
    # 匹配条号
    article_pattern = re.compile(r"第[一二三四五六七八九十百零]+条")

    lines = raw_text.strip().split("\n")
    i = 0

    # 提取法名（如果未提供）
    if not law_name:
        for line in lines:
            if "中华人民共和国" in line and "法" in line:
                law_name = line.strip()
                break

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 检测章标题
        if chapter_pattern.match(line):
            current_chapter = line
            i += 1
            continue

        # 检测条款
        match = article_pattern.match(line)
        if match:
            article_number = match.group()
            # 条款内容可能跨行
            content = line[len(article_number):].strip()
            i += 1
            # 继续读取后续行直到下一个条或章
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                if article_pattern.match(next_line) or chapter_pattern.match(next_line):
                    break
                content += next_line
                i += 1

            articles.append({
                "law_name": law_name,
                "chapter": current_chapter,
                "article_number": article_number,
                "content": content,
            })
        else:
            i += 1

    return articles


def process_case_text(raw_case: dict) -> dict:
    """将案例数据处理为统一结构

    Args:
        raw_case: 原始案例数据字典

    Returns:
        结构化的案例数据，包含 case_id, case_type, crime, fact, judgment, applicable_law
    """
    return {
        "case_id": raw_case.get("case_id", ""),
        "case_type": raw_case.get("case_type", ""),
        "crime": raw_case.get("crime", ""),
        "fact": raw_case.get("fact", ""),
        "judgment": raw_case.get("judgment", ""),
        "applicable_law": raw_case.get("applicable_law", ""),
    }


def batch_process_cases(raw_cases: list[dict]) -> list[dict]:
    """批量处理案例数据"""
    return [process_case_text(case) for case in raw_cases]
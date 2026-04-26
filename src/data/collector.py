"""数据采集模块：下载公开法律法规和案例数据集"""

import json
import urllib.request
from pathlib import Path

from src.config import get_project_root

RAW_DATA_DIR = get_project_root() / "data" / "raw"


def download_cail_dataset(save_path: Path | None = None) -> Path:
    """下载CAIL（中国法律人工智能挑战赛）数据集

    CAIL数据集包含刑法相关案例，来源为GitHub开源发布。
    如下载失败，请手动从 https://github.com/china-ai-law-challenge 下载。
    """
    if save_path is None:
        save_path = RAW_DATA_DIR / "cail_cases.json"

    save_path.parent.mkdir(parents=True, exist_ok=True)

    if save_path.exists():
        return save_path

    # CAIL 2018 数据集的示例URL（实际使用时替换为有效下载链接）
    url = "https://github.com/china-ai-law-challenge/CAIL2018/raw/master/data/data_train.json"

    try:
        urllib.request.urlretrieve(url, save_path)
    except Exception as e:
        print(f"下载失败: {e}")
        print(f"请手动下载数据集到 {save_path}")

    return save_path


def load_sample_laws() -> list[dict]:
    """加载内置的示例法律条文数据

    在没有完整数据集时，使用内置示例数据进行开发测试。
    """
    sample_data = [
        {
            "law_name": "中华人民共和国刑法",
            "chapter": "第二编 分则",
            "article_number": "第二百三十二条",
            "content": "故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑；情节较轻的，处三年以上十年以下有期徒刑。",
        },
        {
            "law_name": "中华人民共和国刑法",
            "chapter": "第二编 分则",
            "article_number": "第二百六十四条",
            "content": "盗窃公私财物，数额较大的，或者多次盗窃、入户盗窃、携带凶器盗窃、扒窃的，处三年以下有期徒刑、拘役或者管制，并处或者单处罚金；数额巨大或者有其他严重情节的，处三年以上十年以下有期徒刑，并处罚金；数额特别巨大或者有其他特别严重情节的，处十年以上有期徒刑或者无期徒刑，并处罚金或者没收财产。",
        },
        {
            "law_name": "中华人民共和国劳动合同法",
            "chapter": "第一章 总则",
            "article_number": "第十条",
            "content": "建立劳动关系，应当订立书面劳动合同。已建立劳动关系，未同时订立书面劳动合同的，应当自用工之日起一个月内订立书面劳动合同。",
        },
        {
            "law_name": "中华人民共和国劳动合同法",
            "chapter": "第七章 法律责任",
            "article_number": "第八十二条",
            "content": "用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。",
        },
        {
            "law_name": "中华人民共和国民法典",
            "chapter": "第一编 总则",
            "article_number": "第一百一十条",
            "content": "自然人享有生命权、身体权、健康权、姓名权、肖像权、名誉权、荣誉权、隐私权、婚姻自主权等权利。法人、非法人组织享有名称权、名誉权和荣誉权。",
        },
    ]
    return sample_data


def load_sample_cases() -> list[dict]:
    """加载内置的示例案例数据"""
    sample_data = [
        {
            "case_id": "CASE001",
            "case_type": "刑事",
            "crime": "故意杀人",
            "fact": "被告人李某因家庭纠纷持刀将被害人王某刺死",
            "judgment": "判处无期徒刑",
            "applicable_law": "刑法第二百三十二条",
        },
        {
            "case_id": "CASE002",
            "case_type": "刑事",
            "crime": "盗窃",
            "fact": "被告人张某多次入户盗窃，盗窃金额累计5万元",
            "judgment": "判处有期徒刑三年，并处罚金",
            "applicable_law": "刑法第二百六十四条",
        },
        {
            "case_id": "CASE003",
            "case_type": "劳动争议",
            "crime": "",
            "fact": "原告入职被告公司6个月，被告未签订书面劳动合同",
            "judgment": "被告支付双倍工资差额",
            "applicable_law": "劳动合同法第八十二条",
        },
    ]
    return sample_data


def save_data(data: list[dict], filename: str) -> Path:
    """保存数据到processed目录"""
    processed_dir = get_project_root() / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    save_path = processed_dir / filename
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return save_path
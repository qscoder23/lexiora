"""专业Agent基类：可复用的领域问答Agent"""

from pathlib import Path

import yaml
from openai import OpenAI

from src.config import load_config, get_project_root
from src.retrieval.fusion import hybrid_search


class DomainAgent:
    """领域专业Agent

    根据领域配置加载对应的系统prompt，调用GraphRAG检索并生成回答。
    """

    def __init__(self, domain: str):
        self.domain = domain
        self.config_data = self._load_domain_config(domain)
        self.system_prompt = self.config_data["system_prompt"]

    def _load_domain_config(self, domain: str) -> dict:
        """加载领域配置文件"""
        config_path = get_project_root() / "src" / "agents" / "config" / f"{domain}.yaml"
        if not config_path.exists():
            # 回退到通用配置
            config_path = get_project_root() / "src" / "agents" / "config" / "general.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def answer(self, question: str, intent: str = "", keywords: list[str] | None = None) -> dict:
        """生成领域专业回答

        Args:
            question: 用户问题
            intent: 意图标签
            keywords: 关键词列表

        Returns:
            包含 answer, sources 的字典
        """
        config = load_config()

        # 1. 检索相关知识
        context_docs = hybrid_search(question)

        # 2. 构建上下文
        context_text = "\n\n".join(
            f"[{i+1}] {doc.page_content}"
            for i, doc in enumerate(context_docs)
        )

        # 3. 调用LLM
        client = OpenAI(
            api_key=config["llm"]["api_key"],
            base_url=config["llm"]["base_url"],
        )

        user_message = f"""参考资料：
{context_text}

用户问题：{question}
问题意图：{intent}
关键词：{', '.join(keywords or [])}

请根据参考资料和专业判断给出回答。"""

        response = client.chat.completions.create(
            model=config["llm"]["model"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=config["llm"]["temperature"],
            max_tokens=config["llm"]["max_tokens"],
        )

        answer = response.choices[0].message.content

        # 4. 整理来源
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
            "domain": self.domain,
            "context_docs": context_docs,
        }
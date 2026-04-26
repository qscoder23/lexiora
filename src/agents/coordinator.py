"""协调Agent：意图识别和领域路由"""

import re
import json

from openai import OpenAI

from src.config import load_config

DOMAINS = ["civil_law", "criminal_law", "labor_law", "admin_law", "general"]

DOMAIN_MAP = {
    "民法": "civil_law",
    "民事": "civil_law",
    "合同": "civil_law",
    "婚姻": "civil_law",
    "继承": "civil_law",
    "侵权": "civil_law",
    "刑法": "criminal_law",
    "刑事": "criminal_law",
    "犯罪": "criminal_law",
    "量刑": "criminal_law",
    "盗窃": "criminal_law",
    "杀人": "criminal_law",
    "劳动": "labor_law",
    "劳动合同": "labor_law",
    "工资": "labor_law",
    "社保": "labor_law",
    "工伤": "labor_law",
    "行政": "admin_law",
    "行政处罚": "admin_law",
    "行政诉讼": "admin_law",
}


def identify_domain(question: str) -> dict:
    """识别用户问题所属的法律领域和意图

    Args:
        question: 用户自然语言问题

    Returns:
        包含 domain, intent, keywords 的字典
    """
    config = load_config()
    client = OpenAI(
        api_key=config["llm"]["api_key"],
        base_url=config["llm"]["base_url"],
    )

    prompt = f"""分析以下法律问题，返回JSON格式：
{{
  "domain": "民事/刑事/劳动/行政/通用 中的一个",
  "intent": "法条查询/案例分析/法律建议/概念解释 中的一个",
  "keywords": ["提取的关键词列表"]
}}

问题：{question}

只返回JSON，不要其他内容。"""

    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    try:
        content = response.choices[0].message.content
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*", "", content)
        result = json.loads(content)
        # 将中文领域映射到内部标识
        domain_zh = result.get("domain", "通用")
        domain_en = "general"
        for zh_key, en_val in DOMAIN_MAP.items():
            if zh_key in domain_zh:
                domain_en = en_val
                break
        result["domain"] = domain_en
        result["domain_zh"] = domain_zh
        return result
    except (json.JSONDecodeError, KeyError):
        return {
            "domain": "general",
            "domain_zh": "通用",
            "intent": "法律建议",
            "keywords": [],
        }


# LangGraph Agent Orchestration
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.agents.domain_agent import DomainAgent


class AgentState(TypedDict):
    """Agent工作流状态"""
    question: str
    history: list[dict]
    domain: str
    domain_zh: str
    intent: str
    keywords: list[str]
    answer: str
    sources: list[str]
    context_docs: list


def route_by_domain(state: AgentState) -> str:
    """根据领域路由到对应Agent节点"""
    return state["domain"]


def identify_intent_node(state: AgentState) -> dict:
    """意图识别节点"""
    question = state["question"]
    history = state.get("history", [])

    # 如果有对话历史，将历史拼接到问题前
    if history:
        history_context = "\n".join(
            f"问：{h['question']}\n答：{h['answer']}"
            for h in history[-3:]  # 最多使用最近3轮对话
        )
        question = f"""对话历史：
{history_context}

当前问题：{question}"""

    result = identify_domain(question)
    return {
        "domain": result["domain"],
        "domain_zh": result["domain_zh"],
        "intent": result["intent"],
        "keywords": result["keywords"],
    }


def create_domain_node(domain: str):
    """创建领域Agent节点函数"""
    def domain_node(state: AgentState) -> dict:
        agent = DomainAgent(domain)
        result = agent.answer(
            question=state["question"],
            intent=state["intent"],
            keywords=state["keywords"],
        )
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "context_docs": result["context_docs"],
        }
    return domain_node


def build_agent_graph() -> StateGraph:
    """构建多Agent工作流图"""
    workflow = StateGraph(AgentState)

    # 添加意图识别节点
    workflow.add_node("identify_intent", identify_intent_node)

    # 添加各领域Agent节点
    for domain in DOMAINS:
        workflow.add_node(domain, create_domain_node(domain))

    # 设置入口
    workflow.set_entry_point("identify_intent")

    # 添加条件路由：从意图识别到对应领域Agent
    workflow.add_conditional_edges(
        "identify_intent",
        route_by_domain,
        {domain: domain for domain in DOMAINS},
    )

    # 所有领域Agent指向结束
    for domain in DOMAINS:
        workflow.add_edge(domain, END)

    return workflow.compile()


def ask_agent(question: str, history: list[dict] | None = None) -> dict:
    """多Agent问答入口函数

    Args:
        question: 用户问题
        history: 对话历史列表，每项包含 question 和 answer

    Returns:
        包含 answer, sources, domain 的字典
    """
    graph = build_agent_graph()
    result = graph.invoke({
        "question": question,
        "history": history or [],
        "domain": "",
        "domain_zh": "",
        "intent": "",
        "keywords": [],
        "answer": "",
        "sources": [],
        "context_docs": [],
    })
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "domain": result["domain"],
        "domain_zh": result["domain_zh"],
    }
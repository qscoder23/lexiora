"""Streamlit入口：仅做展示，逻辑全部在模块中"""

import streamlit as st

from src.agents.coordinator import ask_agent

# 页面配置
st.set_page_config(
    page_title="Lexiora 法律咨询助手",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 优雅深色主题配色
st.markdown("""
<style>
    /* 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

    :root {
        --bg-primary: #0f1419;
        --bg-secondary: #1a1f26;
        --bg-card: #21262d;
        --bg-hover: #292e36;
        --accent-gold: #c9a962;
        --accent-gold-dim: #a68b4b;
        --accent-blue: #4a9eff;
        --accent-red: #f07178;
        --accent-green: #56d364;
        --accent-purple: #a371f7;
        --accent-orange: #ffa657;
        --accent-cyan: #39c5cf;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --text-muted: #6e7681;
        --border: #30363d;
    }

    /* 整体 */
    .stApp {
        background: var(--bg-primary);
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 标题 */
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: 0.02em;
    }

    .subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.05em;
    }

    /* 消息 */
    .user-msg {
        background: var(--accent-blue);
        color: white;
        padding: 0.875rem 1.25rem;
        border-radius: 16px 16px 4px 16px;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .assistant-msg {
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 16px 4px;
        max-width: 80%;
        border: 1px solid var(--border);
        font-size: 0.95rem;
        line-height: 1.7;
    }

    /* 领域标签 */
    .domain-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        border: 1px solid;
    }
    .domain-badge.civil { background: rgba(163,113,247,0.15); color: #a371f7; border-color: rgba(163,113,247,0.3); }
    .domain-badge.criminal { background: rgba(240,113,120,0.15); color: #f07178; border-color: rgba(240,113,120,0.3); }
    .domain-badge.labor { background: rgba(255,166,87,0.15); color: #ffa657; border-color: rgba(255,166,87,0.3); }
    .domain-badge.admin { background: rgba(57,197,207,0.15); color: #39c5cf; border-color: rgba(57,197,207,0.3); }
    .domain-badge.general { background: rgba(139,148,158,0.15); color: #8b949e; border-color: rgba(139,148,158,0.3); }

    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border);
    }

    .sidebar-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
    }

    /* 引用来源 */
    .source-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transition: all 0.15s ease;
    }
    .source-item:hover {
        background: var(--bg-hover);
        border-color: var(--accent-gold-dim);
    }
    .source-num {
        width: 24px;
        height: 24px;
        background: var(--accent-gold);
        color: var(--bg-primary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    .source-text {
        color: var(--text-primary);
        font-size: 0.85rem;
    }

    /* 历史项 */
    .history-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border);
    }
    .history-q {
        color: var(--text-primary);
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* 输入框 */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px rgba(201,169,98,0.15) !important;
    }

    /* 按钮 */
    .stButton > button {
        background: var(--accent-gold) !important;
        color: var(--bg-primary) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: var(--accent-gold-dim) !important;
        transform: translateY(-1px);
    }

    /* 折叠 */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
    }

    /* 滚动条 */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

    /* 分隔线 */
    .stDivider {
        border-color: var(--border);
    }

    /* spinner */
    .stSpinner > div {
        border-color: var(--accent-gold);
    }
</style>
""", unsafe_allow_html=True)


DOMAIN_CLASS = {
    "civil_law": "civil",
    "criminal_law": "criminal",
    "labor_law": "labor",
    "admin_law": "admin",
    "general": "general",
}

DOMAIN_ICONS = {
    "civil_law": "⚖️",
    "criminal_law": "🔨",
    "labor_law": "📋",
    "admin_law": "🏛️",
    "general": "💬",
}


def render_source_card(source: str, idx: int):
    st.markdown(f"""
    <div class="source-item">
        <span class="source-num">{idx + 1}</span>
        <span class="source-text">{source}</span>
    </div>
    """, unsafe_allow_html=True)


def main():
    st.markdown('<h1 class="main-title">⚖️ Lexiora 法律咨询助手</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">多Agent协作 · GraphRAG检索 · 专业知识问答</p>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # === 侧边栏 ===
    with st.sidebar:
        # Logo区
        st.markdown("### ⚖️ Lexiora")
        st.markdown("---")

        # 引用来源
        st.markdown('<p class="sidebar-title">📚 引用来源</p>', unsafe_allow_html=True)
        all_sources = []
        for msg in st.session_state.messages:
            if msg.get("role") == "assistant" and msg.get("sources"):
                all_sources.extend(msg["sources"])

        if all_sources:
            for idx, src in enumerate(list(dict.fromkeys(all_sources))[:8]):
                render_source_card(src, idx)
        else:
            st.markdown(
                "<p style='color: var(--text-muted); font-size: 0.85rem;'>开始对话后显示引用来源</p>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # 对话历史
        st.markdown('<p class="sidebar-title">💬 对话记录</p>', unsafe_allow_html=True)
        if st.session_state.messages:
            for i, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    preview = (msg["content"][:28] + "…") if len(msg["content"]) > 28 else msg["content"]
                    st.markdown(f"<div class='history-item'><span class='history-q'>Q：{preview}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='color: var(--text-muted); font-size: 0.85rem;'>暂无对话记录</p>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # 新建对话
        if st.button("🆕 新建对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # === 主对话区 ===
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                domain = msg.get("domain", "general")
                domain_zh = msg.get("domain_zh", "通用")
                cls = DOMAIN_CLASS.get(domain, "general")
                icon = DOMAIN_ICONS.get(domain, "💬")

                st.markdown(
                    f"<span class='domain-badge {cls}'>{icon} {domain_zh}</span>",
                    unsafe_allow_html=True
                )
                st.markdown(f"<div class='assistant-msg'>{msg['content']}</div>", unsafe_allow_html=True)

                if msg.get("sources"):
                    with st.expander("📖 引用依据"):
                        for src in msg["sources"]:
                            st.markdown(f"- {src}")

    # === 输入 ===
    if prompt := st.chat_input("输入法律问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"<div class='user-msg'>{prompt}</div>", unsafe_allow_html=True)

        # 构建历史
        history = []
        for msg in st.session_state.messages[:-1]:
            if msg["role"] == "user":
                history.append({"question": msg["content"], "answer": ""})
            elif msg["role"] == "assistant" and history:
                history[-1]["answer"] = msg["content"]

        with st.chat_message("assistant"):
            with st.spinner("分析中…"):
                result = ask_agent(prompt, history)

            domain = result.get("domain", "general")
            domain_zh = result.get("domain_zh", "通用")
            cls = DOMAIN_CLASS.get(domain, "general")
            icon = DOMAIN_ICONS.get(domain, "💬")

            st.markdown(
                f"<span class='domain-badge {cls}'>{icon} {domain_zh}</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='assistant-msg'>{result['answer']}</div>", unsafe_allow_html=True)

            if result.get("sources"):
                with st.expander("📖 引用依据"):
                    for src in result["sources"]:
                        st.markdown(f"- {src}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "domain": result.get("domain", "general"),
            "domain_zh": result.get("domain_zh", "通用"),
        })


if __name__ == "__main__":
    main()
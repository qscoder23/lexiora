"""POST /api/chat SSE 流式端点"""
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from backend.services.streamer import step_event, error_event, done_event

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    question = body.get("question", "")
    _history = body.get("history", [])

    async def event_stream():
        try:
            # 步骤1: 意图识别
            from src.agents.coordinator import identify_domain
            domain_result = identify_domain(question)
            yield await step_event(
                "intent", "completed",
                domain=domain_result.get("domain", "general"),
                domain_zh=domain_result.get("domain_zh", "通用"),
                intent=domain_result.get("intent", "")
            )

            # 步骤2: 检索（同步调用）
            from src.retrieval.fusion import hybrid_search
            docs = hybrid_search(question)
            sources_count = len(docs)
            yield await step_event("retrieve", "completed", sources_count=sources_count)

            # 步骤3: 生成（同步调用）
            from src.agents.domain_agent import DomainAgent
            agent = DomainAgent(domain_result.get("domain", "general"))
            result = agent.answer(question, domain_result.get("intent", ""), domain_result.get("keywords", []))

            yield await step_event("generate", "completed", answer=result.get("answer", ""))

            # 完成
            yield await done_event(result.get("sources", []))

        except Exception as e:
            yield await error_event(str(e))

    return EventSourceResponse(event_stream())
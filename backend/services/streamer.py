"""SSE 事件发送器"""
import json

async def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def step_event(step: str, status: str, **kwargs) -> str:
    return await sse_event("step", {"step": step, "status": status, **kwargs})

async def error_event(message: str) -> str:
    return await sse_event("error", {"message": message})

async def done_event(sources: list[str]) -> str:
    return await sse_event("done", {"sources": sources})
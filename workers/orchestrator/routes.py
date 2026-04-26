import anyio
from fastapi import (Depends, 
                     HTTPException, 
                     status, APIRouter, 

                     Header, 
                     BackgroundTasks)
from fastapi.responses import StreamingResponse
from orchestrator.models import AIRequest

orchestrator_router = APIRouter(prefix="/api", tags=["Orchestrator API"])


async def stream_response(query: str, context_id: str) -> str:
    for i in range(10):
        yield b"some fake video bytes"
        await anyio.sleep(20)

@orchestrator_router.post("/task")
async def task(req: AIRequest):
    context_id = f"{req.book_id}:{req.chapter_id}"

    return StreamingResponse(
        stream_response(req.query, context_id),
        media_type="text/plain"
    )
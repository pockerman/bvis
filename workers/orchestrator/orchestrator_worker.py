from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json



app = FastAPI()


@app.post("/task")
async def task(req: AIRequest):
    context_id = f"{req.book_id}:{req.chapter_id}"

    return StreamingResponse(
        stream_response(req.query, context_id),
        media_type="text/plain"
    )
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app = FastAPI()

def generate(text: str):
    for word in text.split():
        yield f"data: {word}\n\n"   # SSE format
        time.sleep(0.1)

@app.get("/stream")
def stream(text: str):
    return StreamingResponse(generate(text), media_type="text/event-stream")
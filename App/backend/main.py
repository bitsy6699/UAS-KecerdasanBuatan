import asyncio, uuid, json, threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

import sys, os
_proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _proj_root)
sys.path.insert(0, os.path.join(_proj_root, 'App'))

from chatbot import PRDChatbot, TEMPLATES


sessions: dict[str, dict] = {}
_chatbot: PRDChatbot | None = None
_model_loading = False
_model_ready = threading.Event()


def _ensure_chatbot():
    global _chatbot, _model_loading
    if _chatbot is not None:
        return _chatbot
    if _model_loading:
        _model_ready.wait()
        return _chatbot
    _model_loading = True
    try:
        _chatbot = PRDChatbot()
    finally:
        _model_ready.set()
    return _chatbot


app = FastAPI(title="loehoer.ai API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str


class StopRequest(BaseModel):
    session_id: str


@app.get("/api/templates")
def get_templates():
    return {
        k: {"label": v["label"], "desc": v["desc"]}
        for k, v in TEMPLATES.items()
    }


@app.post("/api/chat")
def start_chat(req: ChatRequest):
    chatbot = _ensure_chatbot()
    if not chatbot:
        raise HTTPException(503, "Model gagal dimuat")

    chatbot.generate_prd_async(req.prompt)

    session_id = str(uuid.uuid4())
    sessions[session_id] = {"chatbot": chatbot, "done": False}
    return {"session_id": session_id}


@app.get("/api/chat/{session_id}/stream")
async def stream_chat(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    chatbot = session["chatbot"]
    last_len = 0

    async def event_generator():
        nonlocal last_len
        try:
            while True:
                if chatbot.get_error():
                    yield {"event": "error", "data": chatbot.get_error()}
                    return

                current = chatbot.get_partial()
                new_part = current[last_len:]
                if new_part:
                    last_len = len(current)
                    yield {"event": "message", "data": new_part}

                if chatbot.is_done():
                    yield {"event": "done", "data": ""}
                    return

                await asyncio.sleep(0.05)
        finally:
            sessions.pop(session_id, None)

    return EventSourceResponse(event_generator())


@app.post("/api/chat/{session_id}/stop")
def stop_chat(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    session["chatbot"].stop()
    return {"status": "stopped"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

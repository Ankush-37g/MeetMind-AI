"""
MeetMind AI — FastAPI Backend
REST API layer connecting the React frontend to the existing pipeline.
"""

import os
import json
import tempfile
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from database import init_db, save_meeting, get_meetings, get_meeting, delete_meeting, save_chat, get_chats

load_dotenv()

# ── In-memory cache for RAG chains (not serializable) ───────
rag_chains: dict = {}


# ── Lifespan: init DB on startup ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="MeetMind AI API", version="1.0.0", lifespan=lifespan)

# ── CORS — allow React dev server ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ───────────────────────────────
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


# ── Helper: Run blocking pipeline steps in a thread ─────────
async def run_in_thread(func, *args):
    """Run a synchronous function in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


# ── SSE Progress Streaming ──────────────────────────────────
def sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def pipeline_generator(source: str, language: str):
    """
    Run the full MeetMind pipeline and yield SSE progress events.
    The final event contains the complete meeting result + meeting_id.
    """
    try:
        # Step 1: Process audio
        yield sse_event("progress", {"step": 1, "total": 8, "message": "Processing audio..."})
        chunks = await run_in_thread(process_input, source)

        # Step 2: Transcribe
        yield sse_event("progress", {"step": 2, "total": 8, "message": "Transcribing audio..."})
        transcript = await run_in_thread(transcribe_all, chunks, language)

        # Step 3: Generate title
        yield sse_event("progress", {"step": 3, "total": 8, "message": "Generating title..."})
        title = await run_in_thread(generate_title, transcript)

        # Step 4: Summarize
        yield sse_event("progress", {"step": 4, "total": 8, "message": "Summarizing transcript..."})
        summary = await run_in_thread(summarize, transcript)

        # Step 5: Extract action items
        yield sse_event("progress", {"step": 5, "total": 8, "message": "Extracting action items..."})
        action_items = await run_in_thread(extract_action_items, transcript)

        # Step 6: Extract key decisions
        yield sse_event("progress", {"step": 6, "total": 8, "message": "Extracting key decisions..."})
        key_decisions = await run_in_thread(extract_key_decisions, transcript)

        # Step 7: Extract questions
        yield sse_event("progress", {"step": 7, "total": 8, "message": "Extracting open questions..."})
        open_questions = await run_in_thread(extract_questions, transcript)

        # Step 8: Build RAG chain
        yield sse_event("progress", {"step": 8, "total": 8, "message": "Building knowledge base..."})
        rag_chain = await run_in_thread(build_rag_chain, transcript)

        # Calculate metrics
        word_count = len(transcript.split())
        chunks_count = len(chunks)

        # Save to database
        meeting_data = {
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": key_decisions,
            "open_questions": open_questions,
            "language": language,
            "source": source,
            "word_count": word_count,
            "chunks_count": chunks_count,
        }
        meeting_id = save_meeting(meeting_data)

        # Cache the RAG chain in memory
        rag_chains[meeting_id] = rag_chain

        # Final event with all results
        result = {
            "meeting_id": meeting_id,
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": key_decisions,
            "open_questions": open_questions,
            "language": language,
            "word_count": word_count,
            "chunks_count": chunks_count,
        }
        yield sse_event("complete", result)

    except Exception as e:
        yield sse_event("error", {"message": str(e)})


# ── API Endpoints ───────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_meeting(
    source: str = Form(None),
    language: str = Form("english"),
    file: UploadFile = File(None),
):
    """
    Analyze a meeting from a YouTube URL or uploaded file.
    Returns an SSE stream with progress updates.
    """
    if not source and not file:
        raise HTTPException(status_code=400, detail="Provide a YouTube URL or upload a file.")

    # If a file was uploaded, save it to a temp location
    file_path = None
    if file:
        suffix = os.path.splitext(file.filename)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="downloads")
        content = await file.read()
        tmp.write(content)
        tmp.close()
        file_path = tmp.name
        source = file_path

    return StreamingResponse(
        pipeline_generator(source, language),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat/{meeting_id}", response_model=ChatResponse)
async def chat_with_meeting(meeting_id: str, request: ChatRequest):
    """Ask a question about a specific meeting using RAG."""
    # Check if meeting exists
    meeting = get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    # Rebuild RAG chain from vector store if not in cache
    if meeting_id not in rag_chains:
        transcript = meeting["transcript"]
        rag_chain = await run_in_thread(build_rag_chain, transcript)
        rag_chains[meeting_id] = rag_chain

    rag_chain = rag_chains[meeting_id]

    # Get answer
    answer = await run_in_thread(ask_question, rag_chain, request.question)

    # Save to database
    save_chat(meeting_id, "user", request.question)
    save_chat(meeting_id, "assistant", answer)

    return ChatResponse(answer=answer)


@app.get("/api/meetings")
async def list_meetings():
    """List all past meeting analyses."""
    return get_meetings()


@app.get("/api/meetings/{meeting_id}")
async def get_meeting_details(meeting_id: str):
    """Get full details of a specific meeting."""
    meeting = get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    # Also include chat history
    chats = get_chats(meeting_id)
    meeting["chats"] = chats
    return meeting


@app.delete("/api/meetings/{meeting_id}")
async def remove_meeting(meeting_id: str):
    """Delete a meeting and its chat history."""
    # Remove from RAG cache
    rag_chains.pop(meeting_id, None)

    deleted = delete_meeting(meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    return {"message": "Meeting deleted successfully."}


# ── Serve React Frontend (For Production/Docker) ─────────────
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API calls
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
            
        # Serve specific files if they exist (like favicon.svg)
        file_path = f"frontend/dist/{full_path}"
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Fallback to index.html for React Router
        return FileResponse("frontend/dist/index.html")

import streamlit as st
import os
import tempfile
import time
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

# Load environment variables
load_dotenv()

# ── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind AI — Intelligent Meeting Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load External CSS ───────────────────────────────────────
def load_css(file_path: str):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("static/style.css")


# ── Session State Initialization ────────────────────────────
defaults = {
    "result": None,
    "rag_chain": None,
    "chat_history": [],
    "processing": False,
    "current_step": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Helper: HTML Components ─────────────────────────────────
def hero():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🧠 AI-Powered</div>
        <div class="hero-title">MeetMind AI</div>
        <div class="hero-subtitle">
            Transform any meeting recording into actionable insights.<br>
            Summarize, extract decisions, and chat with your transcript.
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(icon: str, title: str, subtitle: str, color: str = "violet"):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon {color}">{icon}</div>
        <div>
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_cards(metrics: list):
    cards_html = ""
    for value, label in metrics:
        cards_html += f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>"""
    st.markdown(f'<div class="metrics-row">{cards_html}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def empty_state(icon: str, text: str, hint: str):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-text">{text}</div>
        <div class="empty-state-hint">{hint}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Processing Pipeline ────────────────────────────────────
def run_pipeline(source: str, language: str):
    """Run the full MeetMind pipeline and store results in session state."""
    st.session_state.processing = True
    progress = st.empty()
    status_container = st.empty()

    steps = [
        ("🎵 Processing audio...", "audio"),
        ("🎙️ Transcribing audio...", "transcribe"),
        ("📌 Generating title...", "title"),
        ("📋 Summarizing transcript...", "summarize"),
        ("✅ Extracting action items...", "actions"),
        ("🔑 Extracting key decisions...", "decisions"),
        ("❓ Extracting open questions...", "questions"),
        ("🔗 Building RAG knowledge base...", "rag"),
    ]

    total = len(steps)
    result = {}

    for i, (label, step_key) in enumerate(steps):
        progress.progress((i) / total, text=label)
        st.session_state.current_step = label

        try:
            if step_key == "audio":
                chunks = process_input(source)
                result["chunks_count"] = len(chunks)

            elif step_key == "transcribe":
                transcript = transcribe_all(chunks, language)
                result["transcript"] = transcript

            elif step_key == "title":
                result["title"] = generate_title(result["transcript"])

            elif step_key == "summarize":
                result["summary"] = summarize(result["transcript"])

            elif step_key == "actions":
                result["action_items"] = extract_action_items(result["transcript"])

            elif step_key == "decisions":
                result["key_decisions"] = extract_key_decisions(result["transcript"])

            elif step_key == "questions":
                result["open_questions"] = extract_questions(result["transcript"])

            elif step_key == "rag":
                rag_chain = build_rag_chain(result["transcript"])
                st.session_state.rag_chain = rag_chain

        except Exception as e:
            progress.empty()
            st.error(f"❌ Error during **{label}**: {e}")
            st.session_state.processing = False
            return

    progress.progress(1.0, text="✅ All done!")
    time.sleep(0.5)
    progress.empty()

    # Calculate metrics
    transcript_text = result.get("transcript", "")
    result["word_count"] = len(transcript_text.split())
    result["char_count"] = len(transcript_text)

    st.session_state.result = result
    st.session_state.processing = False
    st.session_state.chat_history = []


# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <span style="font-size: 2rem;">🧠</span>
        <div style="font-size: 1.15rem; font-weight: 700; background: linear-gradient(135deg, #8b5cf6, #22d3ee);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 4px;">
            MeetMind AI
        </div>
        <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">Intelligent Meeting Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    divider()

    section_header("🎯", "Input Source", "Provide a YouTube URL or upload a file")

    input_method = st.radio(
        "Choose input method",
        ["YouTube URL", "Upload File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    source_path = None

    if input_method == "YouTube URL":
        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
        if url:
            source_path = url.strip()
    else:
        uploaded = st.file_uploader(
            "Upload audio/video",
            type=["mp3", "mp4", "wav", "m4a", "ogg", "webm"],
            label_visibility="collapsed",
        )
        if uploaded:
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(uploaded.name)[1],
            )
            tmp.write(uploaded.read())
            tmp.close()
            source_path = tmp.name
            st.success(f"📁 {uploaded.name}")

    divider()

    section_header("🌐", "Language", "Select the audio language")
    language = st.selectbox(
        "Language",
        ["english", "hinglish"],
        label_visibility="collapsed",
    )

    divider()

    # Start processing button
    process_disabled = source_path is None or st.session_state.processing
    if st.button(
        "🚀  Analyze Meeting" if not st.session_state.processing else "⏳  Processing...",
        use_container_width=True,
        disabled=process_disabled,
    ):
        run_pipeline(source_path, language)
        st.rerun()

    if st.session_state.result:
        divider()
        st.markdown("""
        <div style="text-align:center;">
            <div class="status-pill success">✓ Analysis Complete</div>
        </div>
        """, unsafe_allow_html=True)


# ── Main Content ────────────────────────────────────────────
hero()

if st.session_state.result is None:
    # Empty state — no results yet
    empty_state(
        "🎙️",
        "No meeting analyzed yet",
        "Enter a YouTube URL or upload an audio file from the sidebar to get started.",
    )

else:
    result = st.session_state.result

    # ── Metrics Row ─────────────────────────────────────────
    metric_cards([
        (result.get("chunks_count", "—"), "Audio Chunks"),
        (f'{result.get("word_count", 0):,}', "Words"),
        (f'{result.get("char_count", 0):,}', "Characters"),
        (language.capitalize(), "Language"),
    ])

    st.markdown("")

    # ── Title ───────────────────────────────────────────────
    title_text = result.get("title", "Untitled Meeting")
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding: 1.2rem;">
        <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase;
                    font-weight: 700; letter-spacing: 1px; margin-bottom: 6px;">
            Generated Title
        </div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #f1f5f9;">
            📌 {title_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # ── Tabs for Results ────────────────────────────────────
    tab_summary, tab_actions, tab_decisions, tab_questions, tab_transcript, tab_chat = st.tabs([
        "📋 Summary",
        "✅ Action Items",
        "🔑 Decisions",
        "❓ Questions",
        "📝 Transcript",
        "💬 Chat",
    ])

    # ── Summary Tab ─────────────────────────────────────────
    with tab_summary:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("📋", "Meeting Summary", "AI-generated concise summary", "violet")
        st.markdown(result.get("summary", "No summary available."))
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            "⬇️  Download Summary",
            data=result.get("summary", ""),
            file_name="meeting_summary.md",
            mime="text/markdown",
        )

    # ── Action Items Tab ────────────────────────────────────
    with tab_actions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("✅", "Action Items", "Tasks and responsibilities extracted", "emerald")
        st.markdown(result.get("action_items", "No action items found."))
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Key Decisions Tab ───────────────────────────────────
    with tab_decisions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("🔑", "Key Decisions", "Important decisions made during the meeting", "amber")
        st.markdown(result.get("key_decisions", "No key decisions found."))
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Open Questions Tab ──────────────────────────────────
    with tab_questions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("❓", "Open Questions", "Unresolved topics needing follow-up", "rose")
        st.markdown(result.get("open_questions", "No open questions found."))
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Transcript Tab ──────────────────────────────────────
    with tab_transcript:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("📝", "Full Transcript", "Raw transcription output", "indigo")
        transcript_text = result.get("transcript", "")
        st.markdown(
            f'<div class="transcript-box">{transcript_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            "⬇️  Download Transcript",
            data=transcript_text,
            file_name="transcript.txt",
            mime="text/plain",
        )

    # ── Chat Tab ────────────────────────────────────────────
    with tab_chat:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("💬", "Chat with Your Meeting", "Ask questions about the transcript using RAG", "cyan")

        # Display chat history
        if st.session_state.chat_history:
            chat_html = '<div class="chat-container">'
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    chat_html += f"""
                    <div class="chat-bubble user">
                        <div class="chat-sender user-label">You</div>
                        {msg['content']}
                    </div>"""
                else:
                    chat_html += f"""
                    <div class="chat-bubble assistant">
                        <div class="chat-sender ai-label">MeetMind AI</div>
                        {msg['content']}
                    </div>"""
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding: 2rem; color: #64748b;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💡</div>
                <div style="font-size: 0.88rem;">Ask any question about your meeting transcript.</div>
                <div style="font-size: 0.78rem; margin-top: 4px; color: #475569;">
                    e.g. "What was discussed about the deadline?" or "Who is responsible for the demo?"
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Chat input
        question = st.chat_input("Ask a question about the meeting...")
        if question and st.session_state.rag_chain:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("🤔 Thinking..."):
                answer = ask_question(st.session_state.rag_chain, question)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

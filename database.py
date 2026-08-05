"""
MeetMind AI — SQLite Persistence Layer
Stores meeting analyses and chat history for the React frontend.
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "meetmind.db"


def _get_connection():
    """Create a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist. Called on server startup."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT,
            transcript TEXT,
            summary TEXT,
            action_items TEXT,
            key_decisions TEXT,
            open_questions TEXT,
            language TEXT,
            source TEXT,
            word_count INTEGER DEFAULT 0,
            chunks_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def save_meeting(data: dict) -> str:
    """Save a meeting analysis to the database. Returns the meeting ID."""
    meeting_id = str(uuid.uuid4())
    conn = _get_connection()

    conn.execute(
        """INSERT INTO meetings 
           (id, title, transcript, summary, action_items, key_decisions, 
            open_questions, language, source, word_count, chunks_count, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            meeting_id,
            data.get("title", "Untitled Meeting"),
            data.get("transcript", ""),
            data.get("summary", ""),
            data.get("action_items", ""),
            data.get("key_decisions", ""),
            data.get("open_questions", ""),
            data.get("language", "english"),
            data.get("source", ""),
            data.get("word_count", 0),
            data.get("chunks_count", 0),
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()
    return meeting_id


def get_meetings() -> list:
    """Get all meetings (summary view — without full transcript)."""
    conn = _get_connection()
    rows = conn.execute(
        """SELECT id, title, language, source, word_count, chunks_count, created_at
           FROM meetings ORDER BY created_at DESC"""
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_meeting(meeting_id: str) -> dict | None:
    """Get full details of a specific meeting."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_meeting(meeting_id: str) -> bool:
    """Delete a meeting and its associated chats."""
    conn = _get_connection()
    cursor = conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def save_chat(meeting_id: str, role: str, content: str):
    """Save a single chat message."""
    conn = _get_connection()
    conn.execute(
        "INSERT INTO chats (meeting_id, role, content) VALUES (?, ?, ?)",
        (meeting_id, role, content),
    )
    conn.commit()
    conn.close()


def get_chats(meeting_id: str) -> list:
    """Get all chat messages for a meeting."""
    conn = _get_connection()
    rows = conn.execute(
        """SELECT role, content, created_at FROM chats 
           WHERE meeting_id = ? ORDER BY created_at ASC""",
        (meeting_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

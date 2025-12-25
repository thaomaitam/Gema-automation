"""
History Storage - SQLite-based chat history persistence

Stores chat sessions with messages and file attachments.
Location: ~/.gema/history.db
"""
import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from threading import Lock


@dataclass
class Message:
    """Chat message."""
    id: str
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    files: List[str]  # List of file paths
    timestamp: str


@dataclass
class Session:
    """Chat session."""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


class HistoryStorage:
    """SQLite-based chat history storage."""
    
    _instance = None
    _lock = Lock()
    
    DB_DIR = Path.home() / ".gema"
    DB_FILE = DB_DIR / "history.db"
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._ensure_dir()
        self._init_db()
    
    def _ensure_dir(self):
        """Ensure database directory exists."""
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    files TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)')
            conn.commit()
        print(f"✅ History DB initialized at {self.DB_FILE}")
    
    def create_session(self, title: str = "New Chat") -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute(
                'INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)',
                (session_id, title, now, now)
            )
            conn.commit()
        
        return session_id
    
    def update_session_title(self, session_id: str, title: str):
        """Update session title."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute(
                'UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?',
                (title, now, session_id)
            )
            conn.commit()
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        files: List[str] = None
    ) -> str:
        """Add a message to a session."""
        message_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        files_json = json.dumps(files or [])
        
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute(
                'INSERT INTO messages (id, session_id, role, content, files, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                (message_id, session_id, role, content, files_json, now)
            )
            conn.execute(
                'UPDATE sessions SET updated_at = ? WHERE id = ?',
                (now, session_id)
            )
            conn.commit()
        
        return message_id
    
    def get_sessions(self, limit: int = 50) -> List[Session]:
        """Get all sessions, ordered by most recent."""
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT s.*, COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            return [
                Session(
                    id=row['id'],
                    title=row['title'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    message_count=row['message_count']
                )
                for row in cursor.fetchall()
            ]
    
    def get_messages(self, session_id: str) -> List[Message]:
        """Get all messages in a session."""
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC',
                (session_id,)
            )
            
            return [
                Message(
                    id=row['id'],
                    session_id=row['session_id'],
                    role=row['role'],
                    content=row['content'],
                    files=json.loads(row['files'] or '[]'),
                    timestamp=row['timestamp']
                )
                for row in cursor.fetchall()
            ]
    
    def delete_session(self, session_id: str):
        """Delete a session and all its messages."""
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            conn.commit()
    
    def clear_all(self):
        """Clear all history."""
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute('DELETE FROM messages')
            conn.execute('DELETE FROM sessions')
            conn.commit()

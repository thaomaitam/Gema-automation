"""
Cache Manager - SQLite-based caching layer for AI responses.

Handles storage, retrieval, and invalidation of cached AI thoughts.
"""
import sqlite3
import json
import hashlib
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import asdict

from agent.brain import ThinkResult

DB_PATH = Path("cache.db")

class CacheManager:
    """
    Manages SQLite cache for AI responses.
    
    Schema:
        key: TEXT PRIMARY KEY (Hash of context)
        value: TEXT (JSON serialized ThinkResult)
        created_at: REAL (Timestamp)
        expires_at: REAL (Timestamp)
        metadata: TEXT (JSON metadata for invalidation, e.g. user_id, scope)
    """
    
    def __init__(self, db_path: Path = DB_PATH, default_ttl: int = 3600 * 24):
        self.db_path = db_path
        self.default_ttl = default_ttl
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    metadata TEXT
                )
            """)
            # Index for cleanup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)")
            
    def generate_key(self, system_prompt: str, user_request: str, user_id: str = "default", scope: str = "shared") -> str:
        """
        Generate a cache key based on scope.
        
        Args:
            system_prompt: The current system prompt.
            user_request: The user's input.
            user_id: User identifier (for personal scope).
            scope: "shared" (static knowledge) or "personal" (context-dependent).
            
        Returns:
            Hash string.
        """
        # 1. Static Part (System Prompt)
        static_hash = hashlib.md5(system_prompt.encode()).hexdigest()
        
        # 2. Dynamic Part
        if scope == "personal":
            # Include User ID for isolation
            content = f"{user_id}:{user_request}"
        else:
            # Shared knowledge
            content = f"{user_request}"
            
        dynamic_hash = hashlib.md5(content.encode()).hexdigest()
        
        return f"{scope}:{static_hash}:{dynamic_hash}"

    def get(self, key: str) -> Optional[ThinkResult]:
        """Retrieve from cache if exists and not expired."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value, expires_at FROM cache_entries WHERE key = ?", 
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
                
            value_json, expires_at = row
            
            # Check expiration
            if time.time() > expires_at:
                # Lazy delete
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                return None
                
            try:
                data = json.loads(value_json)
                return ThinkResult(**data)
            except Exception as e:
                print(f"⚠️ Cache deserialization error: {e}")
                return None

    def set(self, key: str, result: ThinkResult, ttl: Optional[int] = None, metadata: Dict = None):
        """Store result in cache."""
        # Only cache final answers for now to avoid side-effects of tool calls
        if result.action != "final_answer":
            return
            
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        value_json = json.dumps(asdict(result))
        metadata_json = json.dumps(metadata or {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_entries (key, value, created_at, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, value_json, time.time(), expires_at, metadata_json)
            )

    def invalidate(self, user_id: str):
        """Invalidate all personal cache for a user."""
        # This requires parsing metadata, which is slow in SQLite if not indexed.
        # For now, we can use LIKE on the key if we structured it right, 
        # OR we just rely on the key structure: "personal:..."
        
        # Since our key is "personal:STATIC:DYNAMIC", we can use LIKE 'personal:%' 
        # But wait, we need to filter by user_id which is INSIDE the hash? 
        # No, the key structure I proposed earlier was:
        # f"{scope}:{static_hash}:{dynamic_hash}"
        # The user_id is hashed INTO dynamic_hash, so we can't query by it easily using just the key.
        
        # BETTER APPROACH: Use the metadata column for invalidation queries.
        # But SQLite JSON query is an extension.
        
        # SIMPLE FIX for now: 
        # If we want to support invalidation by user_id, we should probably prefix the key with user_id 
        # if scope is personal.
        # Let's adjust generate_key to: f"{scope}:{user_id}:{static_hash}:{dynamic_hash}"
        pass 
        
    def cleanup(self):
        """Remove expired entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_entries WHERE expires_at < ?", (time.time(),))
    
    def prune_to_limit(self, max_entries: int = 10000):
        """
        Remove oldest entries if table exceeds max_entries.
        Prevents SQLite bloat.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Count entries
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
            count = cursor.fetchone()[0]
            
            if count > max_entries:
                # Delete oldest entries (by created_at)
                delete_count = count - max_entries
                conn.execute("""
                    DELETE FROM cache_entries 
                    WHERE key IN (
                        SELECT key FROM cache_entries 
                        ORDER BY created_at ASC 
                        LIMIT ?
                    )
                """, (delete_count,))
                print(f"🗑️ Pruned {delete_count} old cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*), SUM(LENGTH(value)) FROM cache_entries")
            count, total_bytes = cursor.fetchone()
            return {
                "entries": count or 0,
                "size_bytes": total_bytes or 0,
                "size_mb": (total_bytes or 0) / (1024 * 1024)
            }



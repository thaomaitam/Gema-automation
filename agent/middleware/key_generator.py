"""
Smart Key Generator V3 - Hybrid Strategy with Lightweight Fingerprinting.

Changes from V2:
1. Removed `turn_index` (redundant with history_hash)
2. Added Hybrid Key Strategy: ContentKey (shared) + ContextKey (personal)
3. Lightweight history fingerprinting using rolling semantic hash
"""
import hashlib
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


# Blacklist: Force cache miss for time-sensitive queries
BLACKLIST_KEYWORDS = [
    # Time (Vietnamese + English)
    "mấy giờ", "thời gian", "hôm nay", "hôm qua", "bây giờ",
    "what time", "current time", "today", "now", "yesterday",
    # Price/Stock
    "giá", "bitcoin", "stock", "price", "crypto", "exchange rate", "tỷ giá",
    # Weather
    "thời tiết", "weather", "nhiệt độ", "temperature",
    # Real-time
    "news", "tin tức", "live", "stream", "real-time", "trending",
]

# Personal indicators: Requires context isolation
PERSONAL_INDICATORS = [
    "tôi", "của mình", "của tao", "tài khoản", "lịch sử", "profile",
    "my", "mine", "i ", "i'", "me ", "account", "history", "favorite",
]

# Technical/Factual indicators: Safe for shared cache
FACTUAL_INDICATORS = [
    # Programming
    "python", "javascript", "rust", "golang", "java", "c++", "typescript",
    "function", "class", "method", "algorithm", "code", "syntax", "error",
    "html", "css", "api", "database", "sql", "json", "regex",
    # Definitions
    "là gì", "what is", "how to", "explain", "define", "tutorial",
    "giải thích", "hướng dẫn", "cách", "làm sao", "tại sao",
]


@dataclass 
class KeyResult:
    """Result from key generation."""
    content_key: Optional[str]  # Shared cache key (content-based only)
    context_key: Optional[str]  # Personal cache key (includes conversation context)
    scope: str  # "shared", "contextual", "blacklisted"
    confidence: float  # 0.0-1.0 confidence in scope detection


class SmartKeyGenerator:
    """
    Generates cache keys with Hybrid Strategy.
    
    V3 Key Formula:
    - ContentKey: Hash(normalized_query) - For shared knowledge
    - ContextKey: Hash(user_id + conversation_id + history_fingerprint + normalized_query)
    
    Read Strategy: Try ContextKey first, fallback to ContentKey
    Write Strategy: Write to appropriate key(s) based on scope detection
    """
    
    def __init__(self, history_window: int = 5):
        self.history_window = history_window
    
    def normalize_query(self, query: str) -> str:
        """Normalize query for better hit rate."""
        normalized = query.lower().strip()
        normalized = re.sub(r'[.?!,;:]+$', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def is_blacklisted(self, query: str) -> bool:
        """Check for time-sensitive keywords."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in BLACKLIST_KEYWORDS)
    
    def detect_scope(self, query: str, history: List[Dict]) -> Tuple[str, float]:
        """
        Detect query scope with confidence score.
        
        Returns:
            (scope, confidence) where scope is "shared" | "contextual" | "blacklisted"
        """
        query_lower = query.lower()
        
        # 1. Blacklist check (highest priority)
        if self.is_blacklisted(query):
            return ("blacklisted", 1.0)
        
        # 2. Count indicators
        personal_score = sum(1 for ind in PERSONAL_INDICATORS if ind in query_lower)
        factual_score = sum(1 for ind in FACTUAL_INDICATORS if ind in query_lower)
        
        # 3. Context check: If there's conversation history, query might be contextual
        has_context = len(history) > 0
        
        # Short query with context = likely follow-up (contextual)
        is_short_query = len(query.split()) <= 5
        
        # 4. Decision logic
        if personal_score > 0:
            return ("contextual", min(0.9 + personal_score * 0.05, 1.0))
        
        if factual_score >= 2:
            # Strong factual indicators = shared
            return ("shared", min(0.7 + factual_score * 0.1, 1.0))
        
        if is_short_query and has_context:
            # Short follow-up question like "còn gì nữa?", "tell me more"
            return ("contextual", 0.8)
        
        if factual_score == 1:
            return ("shared", 0.6)
        
        # Default: If no indicators, assume shared for coding/automation context
        # (This is where we differ from V2's conservative approach)
        return ("shared", 0.5)
    
    def normalize_history_hash(self, history: List[Dict]) -> str:
        """
        Create lightweight fingerprint for conversation history.
        
        Instead of hashing full text, we hash:
        - Role sequence (u=user, a=assistant, t=tool)
        - First 20 chars of each message
        - Total message count
        
        This creates a "shape" of the conversation without storing full content.
        """
        if not history:
            return "empty"
        
        recent = history[-self.history_window:]
        
        # Build fingerprint components
        parts = []
        role_seq = ""
        
        for msg in recent:
            role = msg.get("role", "?")[0].lower()  # u, a, s, t
            role_seq += role
            
            content = msg.get("content", "")
            # Take first 20 chars, normalized
            snippet = re.sub(r'\s+', ' ', content[:20].lower().strip())
            parts.append(snippet)
        
        fingerprint = f"{role_seq}|{len(recent)}|{'|'.join(parts)}"
        return hashlib.md5(fingerprint.encode()).hexdigest()[:12]
    
    def generate_keys(
        self, 
        user_id: str,
        conversation_id: str,
        user_query: str,
        conversation_history: List[Dict],
        system_prompt_hash: str = ""
    ) -> KeyResult:
        """
        Generate both ContentKey and ContextKey.
        
        Returns KeyResult with both keys and detected scope.
        """
        normalized = self.normalize_query(user_query)
        scope, confidence = self.detect_scope(user_query, conversation_history)
        
        # Blacklisted = no caching
        if scope == "blacklisted":
            return KeyResult(
                content_key=None,
                context_key=None,
                scope=scope,
                confidence=confidence
            )
        
        # ContentKey: Pure content-based (for shared cache)
        content_material = f"{system_prompt_hash[:8]}|{normalized}"
        content_key = f"content:{hashlib.sha256(content_material.encode()).hexdigest()[:16]}"
        
        # ContextKey: Includes conversation context
        history_fp = self.normalize_history_hash(conversation_history)
        context_material = f"{user_id}|{conversation_id}|{history_fp}|{normalized}"
        context_key = f"context:{hashlib.sha256(context_material.encode()).hexdigest()[:16]}"
        
        return KeyResult(
            content_key=content_key,
            context_key=context_key,
            scope=scope,
            confidence=confidence
        )


# Singleton
key_generator = SmartKeyGenerator()

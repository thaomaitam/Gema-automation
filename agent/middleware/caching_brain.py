"""
Caching Brain V3 - Hybrid Key Strategy with SQLite Pruning.

Changes from V2:
1. Dual-key read: Try ContextKey first, fallback to ContentKey
2. Dual-key write: Write to appropriate key(s) based on scope
3. SQLite pruning on initialization
"""
import uuid
from typing import Optional, Dict, Any, List
import hashlib

from agent.brain import Brain, ThinkResult
from agent.middleware.cache_manager import CacheManager
from agent.middleware.key_generator import SmartKeyGenerator, KeyResult


class CachingBrain(Brain):
    """
    V3 Caching Brain with Hybrid Key Strategy.
    
    Read Strategy:
    1. Check ContextKey (high precision)
    2. If miss, check ContentKey (shared cache, lower precision for follow-ups)
    
    Write Strategy:
    - Shared scope: Write to ContentKey only
    - Contextual scope: Write to ContextKey only
    - High confidence shared (>=0.7): Write to both
    """
    
    MAX_CACHE_ENTRIES = 10000  # Prune beyond this
    
    def __init__(self, wrapped_brain: Brain, cache_manager: CacheManager, user_id: str = "default"):
        self.wrapped_brain = wrapped_brain
        self.cache_manager = cache_manager
        self.user_id = user_id
        self.key_generator = SmartKeyGenerator(history_window=5)
        
        # Conversation tracking
        self.conversation_id = str(uuid.uuid4())[:8]
        self.conversation_history: List[Dict] = []
        
        # System prompt hash for cache invalidation when prompt changes
        system_prompt = getattr(wrapped_brain, "system_prompt", "")
        self.system_prompt_hash = hashlib.md5(system_prompt.encode()).hexdigest()
        
        # Copy attributes from wrapped brain
        self.model_name = wrapped_brain.model_name
        self.api_key = wrapped_brain.api_key
        
        # Prune on startup
        self._prune_cache()
        
    def _prune_cache(self):
        """Prune old entries to prevent SQLite bloat."""
        try:
            self.cache_manager.cleanup()  # Remove expired entries
            self.cache_manager.prune_to_limit(self.MAX_CACHE_ENTRIES)
        except Exception as e:
            print(f"⚠️ Cache pruning error: {e}")
        
    def think(
        self, 
        user_request: str, 
        screenshot_path: Optional[str] = None, 
        ui_tree: Optional[str] = None
    ) -> ThinkResult:
        """
        Hybrid Key Strategy: Try ContextKey first, then ContentKey.
        """
        # 1. Generate keys
        key_result = self.key_generator.generate_keys(
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            user_query=user_request,
            conversation_history=self.conversation_history,
            system_prompt_hash=self.system_prompt_hash
        )
        
        # 2. Handle blacklist
        if key_result.scope == "blacklisted":
            print(f"⛔ Cache SKIP (blacklisted): {user_request[:30]}...")
            return self._call_and_record(user_request, screenshot_path, ui_tree)
        
        # 3. Try ContextKey first (precise match)
        if key_result.context_key:
            cached = self.cache_manager.get(key_result.context_key)
            if cached:
                print(f"⚡ Cache HIT (context): {key_result.context_key[-8:]}...")
                return cached
        
        # 4. Fallback to ContentKey (shared cache)
        if key_result.content_key and key_result.scope == "shared":
            cached = self.cache_manager.get(key_result.content_key)
            if cached:
                print(f"⚡ Cache HIT (content): {key_result.content_key[-8:]}...")
                return cached
        
        # 5. Cache miss - call real brain
        print(f"🐢 Cache MISS ({key_result.scope}, conf={key_result.confidence:.1f})")
        result = self._call_and_record(user_request, screenshot_path, ui_tree)
        
        # 6. Store in cache based on scope
        if result.action == "final_answer":
            metadata = {
                "user_id": self.user_id,
                "scope": key_result.scope,
                "query": user_request[:50]
            }
            
            if key_result.scope == "shared":
                # Write to ContentKey (shared cache)
                if key_result.content_key:
                    self.cache_manager.set(key_result.content_key, result, metadata=metadata)
                    
                # If high confidence, also write to ContextKey for precision
                if key_result.confidence >= 0.7 and key_result.context_key:
                    self.cache_manager.set(key_result.context_key, result, metadata=metadata)
                    
            elif key_result.scope == "contextual":
                # Write to ContextKey only
                if key_result.context_key:
                    self.cache_manager.set(key_result.context_key, result, metadata=metadata)
        
        return result
    
    def _call_and_record(
        self, 
        user_request: str, 
        screenshot_path: Optional[str], 
        ui_tree: Optional[str]
    ) -> ThinkResult:
        """Call wrapped brain and record conversation."""
        result = self.wrapped_brain.think(user_request, screenshot_path, ui_tree)
        
        # Record conversation for future context
        self.conversation_history.append({
            "role": "user",
            "content": user_request
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": result.content[:200] if result.content else ""
        })
        
        return result

    # --- Delegation Methods ---
    
    def reset(self) -> None:
        """Reset clears conversation context."""
        self.conversation_id = str(uuid.uuid4())[:8]
        self.conversation_history = []
        return self.wrapped_brain.reset()
        
    def update_system_prompt(self, prompt: str) -> None:
        # Update hash when prompt changes (invalidates content cache naturally)
        self.system_prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        return self.wrapped_brain.update_system_prompt(prompt)
        
    def execute_tool(self, tool_name: str, tool_args: dict) -> Dict[str, Any]:
        return self.wrapped_brain.execute_tool(tool_name, tool_args)
        
    def get_tool_names(self) -> List[str]:
        return self.wrapped_brain.get_tool_names()
        
    @property
    def messages(self):
        if hasattr(self.wrapped_brain, "messages"):
            return self.wrapped_brain.messages
        return []

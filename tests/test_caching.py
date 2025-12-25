"""
Test Caching Middleware V3 - Hybrid Key Strategy
"""
import sys
import os
import time
import sqlite3

sys.path.append(os.getcwd())

from agent.brain import Brain, ThinkResult
from agent.middleware.cache_manager import CacheManager
from agent.middleware.caching_brain import CachingBrain
from agent.middleware.key_generator import SmartKeyGenerator


class MockBrain(Brain):
    """Mock brain for testing."""
    def __init__(self):
        self.model_name = "mock-model"
        self.api_key = "mock-key"
        self.system_prompt = "You are a mock brain."
        self.call_count = 0
        
    def think(self, user_request: str, screenshot_path: str = None, ui_tree: str = None) -> ThinkResult:
        self.call_count += 1
        print(f"  🧠 MockBrain call #{self.call_count}")
        return ThinkResult(
            action="final_answer",
            content=f"Answer for: {user_request}"
        )
        
    def reset(self):
        pass


def test_v3_key_generator():
    print("\n=== Test V3 SmartKeyGenerator ===")
    
    gen = SmartKeyGenerator()
    
    # Test scope detection
    print("\n--- Test: Scope Detection ---")
    
    # Shared queries (factual/coding)
    scope, conf = gen.detect_scope("How to center div in CSS?", [])
    assert scope == "shared", f"Expected shared, got {scope}"
    print(f"✅ CSS query -> {scope} (conf={conf:.1f})")
    
    scope, conf = gen.detect_scope("Python function to sort list", [])
    assert scope == "shared"
    print(f"✅ Python query -> {scope} (conf={conf:.1f})")
    
    # Personal queries
    scope, conf = gen.detect_scope("Tài khoản của tôi thế nào?", [])
    assert scope == "contextual"
    print(f"✅ Personal query -> {scope} (conf={conf:.1f})")
    
    # Blacklisted
    scope, conf = gen.detect_scope("Mấy giờ rồi?", [])
    assert scope == "blacklisted"
    print(f"✅ Time query -> {scope}")
    
    # Follow-up with history
    history = [{"role": "user", "content": "Talk about Rust"}, {"role": "assistant", "content": "Rust is..."}]
    scope, conf = gen.detect_scope("Tell me more", history)
    assert scope == "contextual"
    print(f"✅ Follow-up with history -> {scope}")
    
    print("\n--- Test: History Fingerprint ---")
    fp1 = gen.normalize_history_hash([])
    print(f"Empty history: {fp1}")
    
    fp2 = gen.normalize_history_hash(history)
    print(f"With history: {fp2}")
    
    # Same history = same fingerprint
    fp3 = gen.normalize_history_hash(history)
    assert fp2 == fp3
    print("✅ Same history = same fingerprint")


def test_v3_caching_brain():
    print("\n=== Test V3 CachingBrain ===")
    
    db_file = f"test_cache_v3_{int(time.time())}.db"
    print(f"📂 Using DB: {db_file}")
    
    cache_manager = CacheManager(db_path=db_file)
    mock_brain = MockBrain()
    caching_brain = CachingBrain(mock_brain, cache_manager, user_id="test_user")
    
    # Test 1: Shared query - should use ContentKey
    print("\n--- Test 1: Shared Query (First Call) ---")
    res1 = caching_brain.think("How to center div in CSS?")
    assert mock_brain.call_count == 1
    
    print("\n--- Test 2: Same Shared Query (Should HIT ContentKey) ---")
    res2 = caching_brain.think("How to center div in CSS?")
    assert mock_brain.call_count == 1  # Cache hit!
    print("✅ ContentKey cache HIT confirmed!")
    
    # Test 3: Slightly different query (normalized should match)
    print("\n--- Test 3: Normalized Query (Should HIT) ---")
    res3 = caching_brain.think("how to center div in css?")  # lowercase
    assert mock_brain.call_count == 1  # Should still hit
    print("✅ Normalized query HIT!")
    
    # Test 4: Blacklisted query
    print("\n--- Test 4: Blacklisted Query ---")
    res4 = caching_brain.think("Mấy giờ rồi?")
    assert mock_brain.call_count == 2
    res5 = caching_brain.think("Mấy giờ rồi?")
    assert mock_brain.call_count == 3  # Never cached
    print("✅ Blacklist confirmed!")
    
    # Test 5: Cache stats
    print("\n--- Test 5: Cache Stats ---")
    stats = cache_manager.get_stats()
    print(f"📊 Entries: {stats['entries']}, Size: {stats['size_mb']:.3f} MB")
    
    # Cleanup
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except:
            pass
    
    print("\n🎉 All V3 tests passed!")


if __name__ == "__main__":
    test_v3_key_generator()
    test_v3_caching_brain()

# ============================================================
# Planner-Navigator Architecture Configuration
# ============================================================

PLANNER_CONFIG = {
    "provider": "google",
    "model": "gemini-2.5-pro",
    "temperature": 0.7,
    "reasoning_level": "high"  # high/medium/low
}

NAVIGATOR_CONFIG = {
    "provider": "google",
    "model": "gemini-2.5-flash",
    "temperature": 0.1,
    "reasoning_level": "minimal"  # minimal/low
}

GENERAL_CONFIG = {
    "max_steps": 20,
    "max_actions_per_step": 5,
    "failure_tolerance": 3,
    "vision_enabled": True,
    "highlight_actions": True,
    "app_wait_time_ms": 2000,
    "replanning_frequency": 3
}

# Available model options per provider
MODEL_OPTIONS = {
    "google": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
    ],
    "cliproxy": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-claude-sonnet-4-5",
        "gemini-claude-opus-4-5-thinking",
    ]
}

REASONING_LEVELS = ["high", "medium", "low", "minimal"]

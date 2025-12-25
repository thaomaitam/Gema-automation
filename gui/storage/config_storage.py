"""
Config Storage - JSON-based persistent configuration manager

Saves/loads application settings to ~/.gema/config.json
Thread-safe singleton pattern for concurrent access
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock


class ConfigStorage:
    """Persistent configuration storage using JSON file."""
    
    _instance = None
    _lock = Lock()
    
    CONFIG_DIR = Path.home() / ".gema"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    # Default configuration
    DEFAULTS = {
        "general": {
            "max_steps": 20,
            "max_actions_per_step": 5,
            "failure_tolerance": 3,
            "vision_enabled": True,
            "highlight_actions": True,
            "app_wait_time_ms": 2000,
            "replanning_frequency": 3
        },
        "planner": {
            "provider": "cliproxy",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "reasoning_level": "high"
        },
        "navigator": {
            "provider": "cliproxy", 
            "model": "gemini-2.5-flash",
            "temperature": 0.1,
            "reasoning_level": "minimal"
        },
        "providers": [],  # Custom LLM providers
        "system_prompt": None,  # Custom system prompt (None = use default)
    }
    
    def __new__(cls):
        """Singleton pattern - ensure only one instance exists."""
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
        self._config: Dict[str, Any] = {}
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """Ensure config directory exists."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """Load configuration from file."""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                print(f"✅ Config loaded from {self.CONFIG_FILE}")
            else:
                self._config = self.DEFAULTS.copy()
                self._save()
                print(f"📝 Created default config at {self.CONFIG_FILE}")
        except json.JSONDecodeError as e:
            print(f"⚠️ Config file corrupted, using defaults: {e}")
            self._config = self.DEFAULTS.copy()
        except Exception as e:
            print(f"❌ Config load error: {e}")
            self._config = self.DEFAULTS.copy()
    
    def _save(self):
        """Save configuration to file."""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Config save error: {e}")
    
    def load(self) -> Dict[str, Any]:
        """Get full configuration (merge with defaults for missing keys)."""
        result = self.DEFAULTS.copy()
        self._deep_merge(result, self._config)
        return result
    
    def save(self, config: Dict[str, Any]):
        """Save full configuration."""
        with self._lock:
            self._config = config
            self._save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific config value using dot notation (e.g., 'planner.model')."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set a specific config value using dot notation."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save()
    
    def get_providers(self) -> list:
        """Get custom LLM providers."""
        return self._config.get("providers", [])
    
    def add_provider(self, provider: Dict[str, Any]):
        """Add a new custom provider."""
        providers = self._config.get("providers", [])
        # Remove existing provider with same name
        providers = [p for p in providers if p.get("name") != provider.get("name")]
        providers.append(provider)
        self._config["providers"] = providers
        self._save()
    
    def remove_provider(self, name: str):
        """Remove a custom provider by name."""
        providers = self._config.get("providers", [])
        self._config["providers"] = [p for p in providers if p.get("name") != name]
        self._save()
    
    def get_system_prompt(self) -> Optional[str]:
        """Get custom system prompt (None = use default)."""
        return self._config.get("system_prompt")
    
    def set_system_prompt(self, prompt: Optional[str]):
        """Set custom system prompt."""
        self._config["system_prompt"] = prompt
        self._save()
    
    def _deep_merge(self, base: dict, overlay: dict):
        """Deep merge overlay into base dict."""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def reset(self):
        """Reset to default configuration."""
        self._config = self.DEFAULTS.copy()
        self._save()

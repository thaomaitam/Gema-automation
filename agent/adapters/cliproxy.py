"""
OpenAI-Compatible Brain Adapter

A clean framework for any OpenAI-compatible API provider.
Works with: CLIProxy, OpenAI, Anthropic proxy, local servers, etc.
"""
import os
import json
import requests
import base64
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path

from agent.brain import Brain, ThinkResult
from tools import STRUCTURED_TOOLS, TOOL_REGISTRY
from tools.schemas import TOOL_SCHEMAS


# ============================================================
# Tool Schema Converter
# ============================================================

def pydantic_to_openai_schema(model) -> dict:
    """Convert Pydantic model to OpenAI function schema."""
    schema = model.model_json_schema()
    return {
        "type": "object",
        "properties": schema.get("properties", {}),
        "required": schema.get("required", [])
    }


def build_openai_tools() -> List[dict]:
    """Build OpenAI-format tool definitions from registry."""
    tools = []
    for name, func in TOOL_REGISTRY.items():
        description = getattr(func, '__doc__', f"Tool: {name}") or f"Tool: {name}"
        description = description.split('\n')[0]
        
        parameters = (
            pydantic_to_openai_schema(TOOL_SCHEMAS[name])
            if name in TOOL_SCHEMAS
            else {"type": "object", "properties": {}, "required": []}
        )
        
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        })
    return tools


# Pre-build tools at import
OPENAI_TOOLS = build_openai_tools()


# ============================================================
# CLIProxyBrain - OpenAI-Compatible Adapter
# ============================================================

class CLIProxyBrain(Brain):
    """
    OpenAI-compatible API adapter.
    
    Works with any provider that implements OpenAI's /v1/chat/completions API.
    
    Args:
        api_key: API key for authentication
        model_name: Model to use
        base_url: API base URL (default: http://localhost:8317/v1)
        tool_callback: Optional callback for tool events (event, data) -> None
        system_prompt: Custom system prompt (optional)
    """
    
    def __init__(
        self, 
        api_key: str = None, 
        model_name: str = "gemini-2.5-flash",
        base_url: str = "http://localhost:8317/v1",
        tool_callback: Callable[[str, Dict[str, Any]], None] = None,
        system_prompt: str = None
    ):
        api_key = api_key or os.getenv("CLIPROXY_API_KEY", "")
        if not api_key:
            raise ValueError("API key not provided")
        
        super().__init__(api_key, model_name)
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.tool_callback = tool_callback
        self.system_prompt = system_prompt or ""
        self.messages: List[dict] = []
        
        # Initialize with system message if provided
        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        print(f"✅ Initialized @ {self.base_url}")
        print(f"   Model: {model_name}")
    
    # ========================================
    # Main API
    # ========================================
    
    def think(
        self,
        user_request: str,
        screenshot_path: Optional[str] = None,
        ui_tree: Optional[str] = None
    ) -> ThinkResult:
        """
        Process user request with optional vision input.
        
        Args:
            user_request: The user's instruction
            screenshot_path: Optional path to screenshot
            ui_tree: Optional UI hierarchy string
            
        Returns:
            ThinkResult with action and content
        """
        try:
            # Build user message
            user_content = self._build_user_content(user_request, screenshot_path, ui_tree)
            self.messages.append({"role": "user", "content": user_content})
            
            # Call API
            response = self._call_api()
            if not response:
                return ThinkResult(action="error", content="API call failed")
            
            assistant_msg = response.get("choices", [{}])[0].get("message", {})
            tool_calls = assistant_msg.get("tool_calls", [])
            
            # Handle tool calls
            if tool_calls:
                return self._handle_tool_calls(assistant_msg, tool_calls)
            
            # Text-only response
            content = assistant_msg.get("content", "")
            self.messages.append({"role": "assistant", "content": content})
            return ThinkResult(action="final_answer", content=content)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ThinkResult(action="error", content=str(e))
    
    def reset(self) -> None:
        """Reset conversation history."""
        self.messages = []
        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })
    
    def update_system_prompt(self, prompt: str) -> None:
        """Update system prompt dynamically."""
        self.system_prompt = prompt
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = prompt
        elif prompt:
            self.messages.insert(0, {"role": "system", "content": prompt})
    
    # ========================================
    # Private Methods
    # ========================================
    
    def _build_user_content(
        self, 
        text: str, 
        image_path: Optional[str], 
        ui_tree: Optional[str]
    ) -> Any:
        """Build user message content (text or multimodal)."""
        parts = []
        
        # Add image
        if image_path and Path(image_path).exists():
            parts.append({
                "type": "image_url",
                "image_url": {"url": self._encode_image_url(image_path)}
            })
            print(f"👀 Vision: {image_path}")
        
        # Add UI tree context
        if ui_tree:
            parts.append({"type": "text", "text": f"UI: {ui_tree[:1500]}"})
        
        # Add main text
        parts.append({"type": "text", "text": text})
        
        # Return simple string if text-only
        return text if len(parts) == 1 else parts
    
    def _encode_image_url(self, path: str) -> str:
        """Encode image to data URL."""
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        
        ext = Path(path).suffix.lower()
        media_types = {
            ".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"
        }
        media_type = media_types.get(ext, "image/png")
        return f"data:{media_type};base64,{data}"
    
    def _call_api(self) -> Optional[dict]:
        """Make OpenAI-compatible chat completion request."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model_name,
                    "messages": self.messages,
                    "tools": OPENAI_TOOLS,
                    "tool_choice": "auto",
                    "max_tokens": 4096
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def _handle_tool_calls(self, assistant_msg: dict, tool_calls: list) -> ThinkResult:
        """Execute tool calls and get final response."""
        self.messages.append(assistant_msg)
        
        last_tool_name = ""
        last_tool_args = {}
        
        for tc in tool_calls:
            func = tc.get("function", {})
            tool_name = func.get("name", "")
            tool_args = json.loads(func.get("arguments", "{}"))
            tool_call_id = tc.get("id", "")
            
            last_tool_name = tool_name
            last_tool_args = tool_args
            
            print(f"🤖 Calling: {tool_name}({tool_args})")
            
            # Notify: start
            if self.tool_callback:
                self.tool_callback("tool_start", {"name": tool_name, "args": tool_args})
            
            # Execute
            result = self._execute_tool(tool_name, tool_args)
            success = result.get("success", True)
            
            print(f"   {'✅' if success else '❌'} {result.get('message', result.get('error', ''))}")
            
            # Notify: done/failed
            if self.tool_callback:
                self.tool_callback("tool_done" if success else "tool_failed", {
                    "name": tool_name, "args": tool_args, "result": result
                })
            
            # Add result to messages
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result, ensure_ascii=False)
            })
        
        # Get final response
        final = self._call_api()
        if final:
            content = final.get("choices", [{}])[0].get("message", {}).get("content", "")
            self.messages.append({"role": "assistant", "content": content})
            return ThinkResult(
                action="final_answer",
                tool_name=last_tool_name,
                tool_args=last_tool_args,
                content=content
            )
        
        return ThinkResult(action="final_answer", content="Tool executed")
    
    def _execute_tool(self, name: str, args: dict) -> dict:
        """Execute a tool by name."""
        if name in STRUCTURED_TOOLS:
            return STRUCTURED_TOOLS[name](**args)
        if name in TOOL_REGISTRY:
            return TOOL_REGISTRY[name](**args)
        return {"success": False, "error": f"Tool '{name}' not found"}

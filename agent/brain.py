"""
Brain - Abstract interface for Cloud AI providers.

Provides a unified interface for Gemini, Claude, and OpenAI.
Handles tool execution locally while delegating thinking to cloud.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from agent.tool_schema import generate_tool_schemas
from tools import TOOL_REGISTRY


@dataclass
class ThinkResult:
    """Result from Brain.think() method."""
    action: str  # "tool_call" | "final_answer" | "error"
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    content: str = ""
    
    @property
    def is_tool_call(self) -> bool:
        return self.action == "tool_call" and self.tool_name is not None


class Brain(ABC):
    """
    Abstract Base Class for Cloud AI Providers.
    
    Subclasses: GeminiBrain, ClaudeBrain, OpenAIBrain
    
    Usage:
        brain = GeminiBrain(api_key="...")
        result = brain.think("Click on Settings")
        if result.is_tool_call:
            outcome = brain.execute_tool(result.tool_name, result.tool_args)
    """
    
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize Brain with API credentials.
        
        Args:
            api_key: API key for the cloud provider
            model_name: Model identifier (e.g., "gemini-1.5-flash")
        """
        self.api_key = api_key
        self.model_name = model_name
        self.tool_definitions = generate_tool_schemas(TOOL_REGISTRY)
        self.conversation_history: List[Dict] = []
        self.verbose = True
    
    @abstractmethod
    def think(
        self, 
        user_request: str, 
        screenshot_path: Optional[str] = None, 
        ui_tree: Optional[str] = None
    ) -> ThinkResult:
        """
        Send context to Cloud AI and get decision.
        
        Args:
            user_request: User's natural language request
            screenshot_path: Path to current screenshot (optional)
            ui_tree: XML/text representation of UI (optional)
            
        Returns:
            ThinkResult with action type and details
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset conversation history."""
        pass
    
    def update_system_prompt(self, prompt: str) -> None:
        """Update the system prompt."""
        pass
    
    def execute_tool(self, tool_name: str, tool_args: dict) -> Dict[str, Any]:
        """
        Execute tool locally.
        
        Args:
            tool_name: Name of tool from TOOL_REGISTRY
            tool_args: Arguments to pass to tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in TOOL_REGISTRY:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        try:
            if self.verbose:
                args_str = ", ".join(f"{k}={v}" for k, v in tool_args.items())
                print(f"🔧 {tool_name}({args_str})")
            
            result = TOOL_REGISTRY[tool_name](**tool_args)
            
            if self.verbose:
                msg = result.get("message", "") if isinstance(result, dict) else "OK"
                status = "✅" if result.get("success", True) else "❌"
                print(f"   {status} {msg[:60]}")
            
            return result
            
        except Exception as e:
            error = {"success": False, "error": str(e)}
            if self.verbose:
                print(f"   ❌ {e}")
            return error
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return list(TOOL_REGISTRY.keys())


class CloudAgent:
    """
    High-level agent that uses a Brain to complete tasks.
    
    Handles the think-execute loop.
    """
    
    def __init__(self, brain: Brain, max_iterations: int = 10):
        """
        Initialize CloudAgent with a Brain.
        
        Args:
            brain: Brain instance (GeminiBrain, ClaudeBrain, etc.)
            max_iterations: Maximum tool calls per request
        """
        self.brain = brain
        self.max_iterations = max_iterations
        self.verbose = True
    
    @property
    def messages(self) -> List[Dict]:
        """Get conversation history from brain."""
        if hasattr(self.brain, "messages"):
            return self.brain.messages
        return []
    
    def update_system_prompt(self, prompt: str) -> None:
        """Update system prompt via brain."""
        self.brain.update_system_prompt(prompt)
    
    def chat(self, user_input: str, verbose: bool = None, screenshot_path: str = None, privacy_mode: bool = False) -> str:
        """
        Process user request through think-execute loop.
        
        Args:
            user_input: User's natural language request
            verbose: Ignored (uses self.verbose from __init__)
            screenshot_path: Path to current screenshot
            privacy_mode: If True, only send UI tree (no image)
            
        Returns:
            Final response to user
        """
        # Handle meta questions locally
        input_lower = user_input.lower()
        meta_keywords = ["tool nào", "làm được gì", "help", "có thể làm"]
        if any(kw in input_lower for kw in meta_keywords):
            return self._get_capabilities()
        
        # Think-execute loop
        iterations = 0
        ui_tree = None  # Can be populated from device
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # Get AI decision
            img_path = None if privacy_mode else screenshot_path
            result = self.brain.think(user_input, img_path, ui_tree)
            
            if result.action == "final_answer":
                return result.content
            
            if result.action == "error":
                return f"❌ Lỗi: {result.content}"
            
            if result.is_tool_call:
                # Execute tool
                tool_result = self.brain.execute_tool(result.tool_name, result.tool_args or {})
                
                # Format result for next iteration
                user_input = self._format_tool_result(result.tool_name, tool_result)
                
                # Update screenshot if needed
                if result.tool_name in ("press", "click_element", "swipe", "type_text"):
                    # Could refresh screenshot here
                    pass
            else:
                return result.content
        
        return "⚠️ Đã thử quá nhiều lần. Dừng."
    
    def _format_tool_result(self, tool_name: str, result: dict) -> str:
        """Format tool result for AI context."""
        success = result.get("success", True)
        msg = result.get("message", result.get("error", ""))
        status = "✅" if success else "❌"
        return f"Kết quả {tool_name}: {status} {msg}. Tiếp theo?"
    
    def _get_capabilities(self) -> str:
        """Return agent capabilities."""
        return """🤖 Tôi có thể giúp bạn:

📱 **Thiết bị:** Liệt kê, chụp màn hình
📲 **Điều khiển:** Mở app, Back/Home, vuốt, gõ chữ
🎯 **Tương tác:** Click element, scroll, wait

Hãy cho tôi biết bạn muốn làm gì!"""
    
    def reset(self) -> None:
        """Reset conversation."""
        self.brain.reset()

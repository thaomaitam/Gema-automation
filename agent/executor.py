"""
Tool Executor - Routes tool calls to implementations
"""
import json
from typing import Any

from tools import TOOL_REGISTRY


def execute_tool(name: str, arguments: dict) -> dict:
    """
    Execute a tool by name with given arguments.
    
    Args:
        name: Tool name (must exist in TOOL_REGISTRY)
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        dict: Tool execution result
    """
    if name not in TOOL_REGISTRY:
        return {
            "success": False,
            "error": f"Unknown tool: {name}",
            "available_tools": list(TOOL_REGISTRY.keys())
        }
    
    try:
        tool_func = TOOL_REGISTRY[name]
        result = tool_func(**arguments)
        return result
        
    except TypeError as e:
        return {
            "success": False,
            "error": f"Invalid arguments for tool '{name}': {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution failed: {e}"
        }


def format_tool_result(result: dict) -> str:
    """
    Format tool result for display to the model.
    
    Args:
        result: Tool execution result dict
        
    Returns:
        Formatted string representation
    """
    return json.dumps(result, indent=2, ensure_ascii=False)


def get_tool_names() -> list[str]:
    """Get list of all available tool names."""
    return list(TOOL_REGISTRY.keys())


def get_tool_info() -> list[dict]:
    """Get information about all available tools."""
    info = []
    for name, func in TOOL_REGISTRY.items():
        info.append({
            "name": name,
            "description": func.__doc__.split("\n")[0] if func.__doc__ else "No description"
        })
    return info

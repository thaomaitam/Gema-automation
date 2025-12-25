"""
Tool Schema Generator - Auto-convert Python functions to JSON Schema.

Converts TOOL_REGISTRY functions to OpenAI/Gemini/Claude function calling format.
Uses Python's inspect and type hints to generate schemas automatically.
"""
import inspect
from typing import Any, get_type_hints, Optional


def python_type_to_json_type(py_type: Any) -> str:
    """Convert Python type hint to JSON schema type."""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    
    # Handle Optional types
    origin = getattr(py_type, "__origin__", None)
    if origin is not None:
        # Handle Optional[X] which is Union[X, None]
        args = getattr(py_type, "__args__", ())
        if type(None) in args:
            # Get the non-None type
            for arg in args:
                if arg is not type(None):
                    return python_type_to_json_type(arg)
        return "string"
    
    return type_map.get(py_type, "string")


def get_tool_schema(func) -> dict:
    """
    Generate JSON Schema from a Python function.
    
    Uses docstring for description and type hints for parameter types.
    Compatible with OpenAI, Gemini, and Claude function calling formats.
    
    Args:
        func: Python function to generate schema for
        
    Returns:
        dict: JSON Schema in OpenAI function calling format
    """
    sig = inspect.signature(func)
    
    # Get type hints, fallback to empty dict if fails
    try:
        type_hints = get_type_hints(func)
    except Exception:
        type_hints = {}
    
    # Extract description from docstring
    doc = inspect.getdoc(func)
    if doc:
        # Take first line/sentence as description
        description = doc.split("\n")[0].strip()
        if len(description) > 200:
            description = description[:197] + "..."
    else:
        description = f"Execute {func.__name__}"
    
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for name, param in sig.parameters.items():
        # Skip self, cls, and internal params
        if name in ("self", "cls", "device_id", "kwargs", "kw"):
            continue
        
        param_type = type_hints.get(name, str)
        json_type = python_type_to_json_type(param_type)
        
        # Build property definition
        prop = {"type": json_type}
        
        # Add enum for known parameters
        if name == "direction":
            prop["enum"] = ["up", "down", "left", "right"]
            prop["description"] = "Swipe direction"
        elif name == "orientation":
            prop["enum"] = ["natural", "left", "right", "upsidedown"]
            prop["description"] = "Screen orientation"
        else:
            prop["description"] = f"Parameter: {name}"
        
        parameters["properties"][name] = prop
        
        # If no default value, it's required
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(name)
    
    return {
        "name": func.__name__,
        "description": description,
        "parameters": parameters
    }


def generate_tool_schemas(registry: dict) -> list[dict]:
    """
    Convert entire TOOL_REGISTRY to list of JSON Schemas.
    
    Args:
        registry: Dict mapping tool names to functions
        
    Returns:
        List of JSON Schema dicts for function calling
    """
    schemas = []
    skipped = []
    
    for name, func in registry.items():
        try:
            schema = get_tool_schema(func)
            schemas.append(schema)
        except Exception as e:
            skipped.append(f"{name}: {e}")
    
    if skipped:
        print(f"⚠️ Skipped {len(skipped)} tools: {skipped[:3]}...")
    
    return schemas


def get_tools_for_gemini(registry: dict) -> list[dict]:
    """
    Convert TOOL_REGISTRY to Gemini function declarations format.
    
    Gemini uses a slightly different structure than OpenAI.
    """
    schemas = generate_tool_schemas(registry)
    
    # Gemini format wraps in "function_declarations"
    gemini_tools = []
    for schema in schemas:
        gemini_tools.append({
            "name": schema["name"],
            "description": schema["description"],
            "parameters": schema["parameters"]
        })
    
    return gemini_tools


def get_tools_for_openai(registry: dict) -> list[dict]:
    """
    Convert TOOL_REGISTRY to OpenAI function calling format.
    """
    schemas = generate_tool_schemas(registry)
    
    openai_tools = []
    for schema in schemas:
        openai_tools.append({
            "type": "function",
            "function": schema
        })
    
    return openai_tools


def get_tools_for_claude(registry: dict) -> list[dict]:
    """
    Convert TOOL_REGISTRY to Claude tool use format.
    
    Claude uses "input_schema" instead of "parameters".
    """
    schemas = generate_tool_schemas(registry)
    
    claude_tools = []
    for schema in schemas:
        claude_tools.append({
            "name": schema["name"],
            "description": schema["description"],
            "input_schema": schema["parameters"]
        })
    
    return claude_tools

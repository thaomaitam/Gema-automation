"""
StructuredTool - Wrapper for Pydantic validation on tools.

Provides "Fail Fast" validation before executing tool functions.
Acts as the Contract between AI and Tools.
"""
from typing import Callable, Type, Any, Dict
from pydantic import BaseModel, ValidationError
import functools


class StructuredTool:
    """
    Wrapper that adds Pydantic validation to tool functions.
    
    Benefits:
    - Fail Fast: Catch invalid args before ADB execution
    - Type Safety: Ensure correct data types
    - Documentation: Auto-generate descriptions from schema
    
    Usage:
        tool = StructuredTool(
            name="press",
            func=press,
            args_schema=PressArgs
        )
        result = tool(x=100, y=200)  # Validates before calling
    """
    
    def __init__(
        self, 
        name: str, 
        func: Callable, 
        args_schema: Type[BaseModel],
        description: str = None
    ):
        self.name = name
        self.func = func
        self.args_schema = args_schema
        self.description = description or func.__doc__ or f"Execute {name}"
        
        # Copy function metadata for Google SDK compatibility
        functools.update_wrapper(self, func)
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Validate args with Pydantic, then execute function.
        
        Returns:
            Tool result dict with success/error status
        """
        try:
            # 1. Validate with Pydantic (Fail Fast!)
            validated = self.args_schema(**kwargs)
            
            # 2. Execute function with clean data
            result = self.func(**validated.model_dump(exclude_none=True))
            
            # 3. Ensure result is dict
            if not isinstance(result, dict):
                result = {"success": True, "result": result}
            
            return result
            
        except ValidationError as e:
            # Pydantic validation failed - return immediately
            errors = e.errors()
            msg = "; ".join(f"{err['loc'][0]}: {err['msg']}" for err in errors)
            return {
                "success": False, 
                "error": f"Validation Error: {msg}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution Error: {str(e)}"
            }
    
    def to_openai_schema(self) -> dict:
        """Generate OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema()
            }
        }
    
    def to_gemini_tool(self):
        """Return function for Gemini SDK (auto function calling)."""
        # Gemini SDK can use the wrapped function directly
        # Validation happens in __call__
        return self


def create_structured_tools(registry: dict, schemas: dict) -> dict:
    """
    Create StructuredTools from registry and schemas.
    
    Args:
        registry: Dict of {name: function}
        schemas: Dict of {name: PydanticModel}
        
    Returns:
        Dict of {name: StructuredTool}
    """
    tools = {}
    
    for name, func in registry.items():
        schema = schemas.get(name)
        if schema:
            tools[name] = StructuredTool(
                name=name,
                func=func,
                args_schema=schema
            )
        else:
            # No schema - wrap with NoArgs
            from tools.schemas import NoArgs
            tools[name] = StructuredTool(
                name=name,
                func=func,
                args_schema=NoArgs
            )
    
    return tools

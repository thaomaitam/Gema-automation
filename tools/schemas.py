"""
Pydantic Schemas for Tool Arguments.

Provides validation, auto-documentation, and JSON Schema generation.
Used by Google SDK for function calling and by StructuredTool for validation.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


# ============ Navigation Tools ============

class PressArgs(BaseModel):
    """Tap vào tọa độ trên màn hình Android."""
    x: int = Field(..., ge=0, le=2160, description="Tọa độ X (pixels)")
    y: int = Field(..., ge=0, le=3840, description="Tọa độ Y (pixels)")


class LongPressArgs(BaseModel):
    """Long press tại tọa độ."""
    x: int = Field(..., ge=0, description="Tọa độ X")
    y: int = Field(..., ge=0, description="Tọa độ Y")
    duration: float = Field(default=1.0, ge=0.1, le=10, description="Thời gian giữ (giây)")


class SwipeArgs(BaseModel):
    """Vuốt màn hình theo hướng."""
    direction: Literal["up", "down", "left", "right"] = Field(
        ..., description="Hướng vuốt"
    )


class TypeTextArgs(BaseModel):
    """Gõ chữ vào input đang focus."""
    text: str = Field(..., min_length=1, description="Nội dung cần gõ")


# ============ App Management ============

class AppStartArgs(BaseModel):
    """Mở ứng dụng theo package name."""
    package_name: str = Field(
        ..., 
        description="Package của app (vd: com.facebook.katana, com.zing.zalo)"
    )


class AppStopArgs(BaseModel):
    """Đóng ứng dụng."""
    package_name: str = Field(..., description="Package của app cần đóng")


# ============ Element Interaction ============

class ClickElementArgs(BaseModel):
    """Click vào element theo text hoặc resource-id."""
    text: Optional[str] = Field(default=None, description="Text hiển thị của element")
    resource_id: Optional[str] = Field(default=None, description="Resource ID của element")
    class_name: Optional[str] = Field(default=None, description="Class name (vd: android.widget.Button)")


class WaitElementArgs(BaseModel):
    """Đợi element xuất hiện."""
    text: Optional[str] = Field(default=None, description="Text của element cần đợi")
    resource_id: Optional[str] = Field(default=None, description="Resource ID cần đợi")
    timeout: float = Field(default=10, ge=1, le=60, description="Timeout (giây)")


class SetElementTextArgs(BaseModel):
    """Nhập text vào element."""
    text: str = Field(..., description="Text cần nhập")
    resource_id: Optional[str] = Field(default=None, description="Resource ID của input")


# ============ No-Args Tools ============

class NoArgs(BaseModel):
    """Tool không cần arguments."""
    pass


# ============ Mapping for easy access ============

TOOL_SCHEMAS = {
    # Navigation
    "press": PressArgs,
    "long_press": LongPressArgs,
    "swipe": SwipeArgs,
    "type_text": TypeTextArgs,
    
    # App Management
    "app_start": AppStartArgs,
    "app_stop": AppStopArgs,
    
    # Element
    "click_element": ClickElementArgs,
    "wait_element": WaitElementArgs,
    "set_element_text": SetElementTextArgs,
    
    # No-args tools
    "press_back": NoArgs,
    "press_home": NoArgs,
    "take_screenshot": NoArgs,
    "list_emulators": NoArgs,
}

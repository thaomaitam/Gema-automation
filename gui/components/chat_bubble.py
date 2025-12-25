"""
Chat Bubble Component
Displays chat messages with tool execution indicators
Enhanced with timestamp and better visual differentiation
"""
import customtkinter as ctk
from typing import Optional, Dict, Any
from datetime import datetime

from gui.styles import Colors, Fonts, Dimensions


class ChatBubble(ctk.CTkFrame):
    """Chat message bubble with tool execution display and timestamp"""
    
    def __init__(
        self, 
        parent, 
        message: str, 
        is_user: bool, 
        tool_info: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.message = message
        self.is_user = is_user
        self.tool_info = tool_info
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        
        self._create_bubble()
    
    def _create_bubble(self):
        """Build bubble UI"""
        # Determine alignment and colors
        if self.is_user:
            bubble_color = Colors.ACCENT_PRIMARY
            text_color = "#ffffff"
            align = "e"  # Right align
        else:
            bubble_color = Colors.BG_TERTIARY
            text_color = Colors.TEXT_PRIMARY
            align = "w"  # Left align
        
        # Tool execution indicator (if present)
        if self.tool_info:
            self._create_tool_indicator(align)
        
        # Message bubble
        bubble = ctk.CTkFrame(
            self, 
            fg_color=bubble_color, 
            corner_radius=12
        )
        bubble.pack(anchor=align, padx=Dimensions.PAD_MD, pady=Dimensions.PAD_XS)
        
        # Message text with wrapping
        msg_label = ctk.CTkLabel(
            bubble, 
            text=self.message, 
            wraplength=350, 
            justify="left",
            font=Fonts.body(),
            text_color=text_color
        )
        msg_label.pack(padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
        
        # Timestamp below bubble
        time_label = ctk.CTkLabel(
            self,
            text=self.timestamp,
            font=Fonts.caption(),
            text_color=Colors.TEXT_DISABLED
        )
        time_label.pack(anchor=align, padx=Dimensions.PAD_LG)
    
    def _create_tool_indicator(self, align: str):
        """Create tool execution indicator"""
        tool_frame = ctk.CTkFrame(
            self, 
            fg_color=Colors.BG_SECONDARY, 
            corner_radius=Dimensions.RADIUS_SM
        )
        tool_frame.pack(anchor=align, padx=Dimensions.PAD_MD, pady=Dimensions.PAD_XS)
        
        # Determine status icon and color
        success = self.tool_info.get("success", True)
        icon = "✅" if success else "❌"
        tool_name = self.tool_info.get("name", "Tool")
        
        status_color = Colors.ACCENT_SUCCESS if success else Colors.ACCENT_ERROR
        
        # Tool name with icon
        ctk.CTkLabel(
            tool_frame, 
            text=f"🔧 {tool_name} {icon}",
            font=Fonts.small(),
            text_color=status_color
        ).pack(padx=Dimensions.PAD_MD, pady=Dimensions.PAD_SM)


class TypingIndicator(ctk.CTkFrame):
    """Animated typing indicator for AI responses"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        bubble = ctk.CTkFrame(
            self, 
            fg_color=Colors.BG_TERTIARY, 
            corner_radius=12
        )
        bubble.pack(anchor="w", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_XS)
        
        # Dots container
        dots_frame = ctk.CTkFrame(bubble, fg_color="transparent")
        dots_frame.pack(padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
        
        self.dots = []
        for i in range(3):
            dot = ctk.CTkLabel(
                dots_frame,
                text="●",
                font=(Fonts.FAMILY, 14),
                text_color=Colors.TEXT_SECONDARY
            )
            dot.pack(side="left", padx=2)
            self.dots.append(dot)
        
        self._current_dot = 0
        self._animate()
    
    def _animate(self):
        """Animate the typing dots"""
        # Reset all dots to dim
        for dot in self.dots:
            dot.configure(text_color=Colors.TEXT_DISABLED)
        
        # Highlight current dot
        self.dots[self._current_dot].configure(text_color=Colors.ACCENT_PRIMARY)
        
        # Move to next dot
        self._current_dot = (self._current_dot + 1) % 3
        
        # Schedule next animation frame
        self.after(400, self._animate)


class ChatSession(ctk.CTkScrollableFrame):
    """Container for chat history with auto-scroll"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_PRIMARY,
            corner_radius=Dimensions.RADIUS_MD,
            **kwargs
        )
        
        self._typing_indicator: Optional[TypingIndicator] = None
    
    def add_message(
        self, 
        text: str, 
        is_user: bool, 
        tool_info: Optional[Dict[str, Any]] = None
    ):
        """Add a message to the chat"""
        # Remove typing indicator if present
        if self._typing_indicator:
            self._typing_indicator.destroy()
            self._typing_indicator = None
        
        bubble = ChatBubble(self, message=text, is_user=is_user, tool_info=tool_info)
        bubble.pack(fill="x", pady=Dimensions.PAD_XS)
        
        # Auto scroll to bottom
        self._parent_canvas.yview_moveto(1.0)
    
    def show_typing(self):
        """Show typing indicator"""
        if not self._typing_indicator:
            self._typing_indicator = TypingIndicator(self)
            self._typing_indicator.pack(fill="x", pady=Dimensions.PAD_XS)
            self._parent_canvas.yview_moveto(1.0)
    
    def hide_typing(self):
        """Hide typing indicator"""
        if self._typing_indicator:
            self._typing_indicator.destroy()
            self._typing_indicator = None
    
    def add_divider(self, text: str = "Previous Session"):
        """Add a section divider"""
        divider = ctk.CTkFrame(self, fg_color="transparent")
        divider.pack(fill="x", pady=Dimensions.PAD_MD)
        
        # Left line
        ctk.CTkFrame(divider, fg_color=Colors.DIVIDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(Dimensions.PAD_MD, Dimensions.PAD_SM)
        )
        
        # Text
        ctk.CTkLabel(
            divider,
            text=text,
            font=Fonts.caption(),
            text_color=Colors.TEXT_DISABLED
        ).pack(side="left")
        
        # Right line
        ctk.CTkFrame(divider, fg_color=Colors.DIVIDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(Dimensions.PAD_SM, Dimensions.PAD_MD)
        )
    
    def clear(self):
        """Clear all messages"""
        for widget in self.winfo_children():
            widget.destroy()
        self._typing_indicator = None

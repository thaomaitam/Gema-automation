"""
Agent Panel Component
Main interaction panel with Chat/Plan tabs and input area
"""
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from pathlib import Path

from gui.styles import Colors, Fonts, Dimensions, Styles
from gui.components.chat_bubble import ChatBubble, TypingIndicator
from gui.components.plan_viewer import PlanViewer, StepStatus


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PLANNING = "planning"
    NAVIGATING = "navigating"


class AgentPanel(ctk.CTkFrame):
    """Main agent interaction panel with Chat/Plan tabs"""
    
    STATUS_LABELS = {
        AgentStatus.IDLE: ("🟢 Idle", Colors.STATUS_IDLE),
        AgentStatus.PLANNING: ("🧠 Planning...", Colors.STATUS_PLANNING),
        AgentStatus.NAVIGATING: ("🚀 Navigating...", Colors.STATUS_NAVIGATING),
    }
    
    def __init__(
        self, 
        parent,
        on_send: Callable[[str], None] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color=Colors.BG_SECONDARY, **kwargs)
        
        self.on_send = on_send
        self._status = AgentStatus.IDLE
        self._is_processing = False
        self._attached_files: List[Path] = []  # Files to attach with next message
        
        self._create_header()
        self._create_tabview()
        self._create_input_area()
    
    def _create_header(self):
        """Create header with status indicator"""
        self.header = ctk.CTkFrame(self, fg_color=Colors.BG_TERTIARY, height=50)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        # Logo/Title
        ctk.CTkLabel(
            self.header,
            text="☁️ Gema Agent",
            font=Fonts.subheading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
        
        # Status indicator
        status_label, status_color = self.STATUS_LABELS[self._status]
        self.status_indicator = ctk.CTkLabel(
            self.header,
            text=status_label,
            font=Fonts.small(),
            text_color=status_color
        )
        self.status_indicator.pack(side="right", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
    
    def _create_tabview(self):
        """Create tabbed interface for Chat/Plan"""
        # Tab buttons container
        tab_buttons = ctk.CTkFrame(self, fg_color="transparent", height=40)
        tab_buttons.pack(fill="x", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_SM)
        
        self._active_tab = "chat"
        
        # Chat tab button
        self.chat_tab_btn = ctk.CTkButton(
            tab_buttons,
            text="💬 Chat",
            command=lambda: self._switch_tab("chat"),
            **Styles.tab_button_active()
        )
        self.chat_tab_btn.pack(side="left", padx=Dimensions.PAD_XS)
        
        # Plan tab button
        self.plan_tab_btn = ctk.CTkButton(
            tab_buttons,
            text="📋 Plan",
            command=lambda: self._switch_tab("plan"),
            **Styles.tab_button_inactive()
        )
        self.plan_tab_btn.pack(side="left", padx=Dimensions.PAD_XS)
        
        # Content container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=Dimensions.PAD_SM, pady=Dimensions.PAD_SM)
        
        # Chat view
        self.chat_view = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=Colors.BG_PRIMARY,
            corner_radius=Dimensions.RADIUS_MD
        )
        self.chat_view.pack(fill="both", expand=True)
        
        # Plan view (hidden initially)
        self.plan_view = PlanViewer(self.content_frame)
        
        # Welcome message
        self._show_welcome()
    
    def _create_input_area(self):
        """Create input area with send button"""
        input_container = ctk.CTkFrame(self, fg_color=Colors.BG_TERTIARY, height=70)
        input_container.pack(fill="x", side="bottom")
        input_container.pack_propagate(False)
        
        # Inner container with rounded corners
        inner = ctk.CTkFrame(
            input_container, 
            fg_color=Colors.BG_INPUT,
            corner_radius=Dimensions.RADIUS_FULL
        )
        inner.pack(fill="both", expand=True, padx=Dimensions.PAD_MD, pady=Dimensions.PAD_MD)
        
        # Input entry
        self.input_entry = ctk.CTkEntry(
            inner,
            placeholder_text="What can I help you with?",
            font=Fonts.body(),
            border_width=0,
            fg_color="transparent",
            text_color=Colors.TEXT_PRIMARY
        )
        self.input_entry.pack(side="left", fill="both", expand=True, padx=Dimensions.PAD_LG)
        self.input_entry.bind("<Return>", lambda e: self._handle_send())
        
        # Attach button (file upload)
        self.attach_btn = ctk.CTkButton(
            inner,
            text="📎",
            width=40,
            height=40,
            corner_radius=Dimensions.RADIUS_FULL,
            fg_color="transparent",
            hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_SECONDARY,
            command=self._handle_attach
        )
        self.attach_btn.pack(side="left", padx=Dimensions.PAD_XS)
        
        # Files indicator (shows count when files attached)
        self.files_indicator = ctk.CTkLabel(
            inner,
            text="",
            font=Fonts.small(),
            text_color=Colors.ACCENT_PRIMARY
        )
        self.files_indicator.pack(side="left")
        
        # Send button
        self.send_btn = ctk.CTkButton(
            inner,
            text="↑",
            width=40,
            height=40,
            corner_radius=Dimensions.RADIUS_FULL,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color="#5d8ed9",
            command=self._handle_send
        )
        self.send_btn.pack(side="right", padx=Dimensions.PAD_SM, pady=Dimensions.PAD_XS)
    
    def _switch_tab(self, tab: str):
        """Switch between Chat and Plan tabs"""
        self._active_tab = tab
        
        if tab == "chat":
            self.chat_tab_btn.configure(**Styles.tab_button_active())
            self.plan_tab_btn.configure(**Styles.tab_button_inactive())
            self.plan_view.pack_forget()
            self.chat_view.pack(fill="both", expand=True)
        else:
            self.chat_tab_btn.configure(**Styles.tab_button_inactive())
            self.plan_tab_btn.configure(**Styles.tab_button_active())
            self.chat_view.pack_forget()
            self.plan_view.pack(fill="both", expand=True)
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome_frame = ctk.CTkFrame(self.chat_view, fg_color="transparent")
        welcome_frame.pack(expand=True, pady=Dimensions.PAD_2XL * 2)
        
        ctk.CTkLabel(
            welcome_frame, 
            text="☁️", 
            font=("Segoe UI Emoji", 60)
        ).pack(pady=Dimensions.PAD_MD)
        
        ctk.CTkLabel(
            welcome_frame, 
            text="Gema Cloud Automation",
            font=Fonts.heading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(pady=Dimensions.PAD_SM)
        
        ctk.CTkLabel(
            welcome_frame, 
            text="Powered by Gemini AI • Type a command to begin",
            font=Fonts.body(),
            text_color=Colors.TEXT_SECONDARY
        ).pack()
    
    def _handle_attach(self):
        """Handle file attachment"""
        files = filedialog.askopenfilenames(
            title="Select Files to Attach",
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.png;*.jpg;*.jpeg;*.gif;*.webp"),
                ("Documents", "*.pdf;*.doc;*.docx;*.txt"),
            ]
        )
        if files:
            self._attached_files.extend([Path(f) for f in files])
            self._update_files_indicator()
    
    def _update_files_indicator(self):
        """Update the files indicator label"""
        count = len(self._attached_files)
        if count > 0:
            self.files_indicator.configure(text=f"{count} file(s)")
            self.attach_btn.configure(text_color=Colors.ACCENT_PRIMARY)
        else:
            self.files_indicator.configure(text="")
            self.attach_btn.configure(text_color=Colors.TEXT_SECONDARY)
    
    def _handle_send(self):
        """Handle send button click"""
        if self._is_processing:
            return
        
        message = self.input_entry.get().strip()
        if not message and not self._attached_files:
            return
        
        self.input_entry.delete(0, "end")
        attached = self._attached_files.copy()
        self._attached_files.clear()
        self._update_files_indicator()
        
        if self.on_send:
            self.on_send(message, attached)
    
    # ============================================================
    # Public API
    # ============================================================
    
    def add_message(self, message: str, is_user: bool, tool_info: Optional[Dict[str, Any]] = None):
        """Add a message to the chat view"""
        # Skip empty messages
        if not message or not message.strip():
            return
        
        # Clear welcome if first real message
        children = self.chat_view.winfo_children()
        if len(children) == 1 and isinstance(children[0], ctk.CTkFrame):
            # Likely welcome frame
            for child in children:
                child.destroy()
        
        bubble = ChatBubble(self.chat_view, message, is_user, tool_info)
        bubble.pack(fill="x", pady=Dimensions.PAD_XS)
        
        # Scroll to bottom
        self.chat_view._parent_canvas.yview_moveto(1.0)
    
    def set_status(self, status: AgentStatus):
        """Update agent status indicator"""
        self._status = status
        label, color = self.STATUS_LABELS[status]
        self.status_indicator.configure(text=label, text_color=color)
    
    def set_processing(self, is_processing: bool):
        """Set processing state (enable/disable input)"""
        self._is_processing = is_processing
        state = "disabled" if is_processing else "normal"
        self.send_btn.configure(state=state)
        
        if is_processing:
            self.set_status(AgentStatus.NAVIGATING)
        else:
            self.set_status(AgentStatus.IDLE)
    
    def add_plan_step(self, description: str) -> int:
        """Add a step to the plan viewer"""
        return self.plan_view.add_step(description)
    
    def update_plan_step(self, step_number: int, status: StepStatus):
        """Update plan step status"""
        self.plan_view.update_step_status(step_number, status)
    
    def set_plan(self, steps: list):
        """Set entire plan at once"""
        self.plan_view.set_plan(steps)
        # Auto-switch to plan tab
        self._switch_tab("plan")
    
    def clear_chat(self):
        """Clear chat history"""
        for widget in self.chat_view.winfo_children():
            widget.destroy()
        self._show_welcome()
    
    def clear_plan(self):
        """Clear plan steps"""
        self.plan_view.clear()

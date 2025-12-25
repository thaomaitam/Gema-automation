"""
Plan Viewer Component - Planner-Navigator Architecture
Displays high-level Plan steps with reasoning (Nanobrowser Style)
"""
import customtkinter as ctk
from typing import List, Dict, Optional, Callable
from enum import Enum

from gui.styles import Colors, Fonts, Dimensions


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanStepItem(ctk.CTkFrame):
    """Individual plan step with step number badge and reasoning display"""
    
    def __init__(
        self, 
        master, 
        step_number: int, 
        title: str, 
        reasoning: str = "",
        **kwargs
    ):
        super().__init__(
            master, 
            fg_color=Colors.BG_TERTIARY, 
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs
        )
        
        self.step_number = step_number
        self._status = StepStatus.PENDING
        
        self.grid_columnconfigure(1, weight=1)
        self._create_widgets(title, reasoning)
    
    def _create_widgets(self, title: str, reasoning: str):
        """Build step UI with badge, title, reasoning, and status icon"""
        
        # 1. Step Number Badge (Circle)
        self.badge = ctk.CTkLabel(
            self,
            text=str(self.step_number),
            width=28,
            height=28,
            fg_color=Colors.BG_HOVER,
            corner_radius=14,
            text_color=Colors.TEXT_PRIMARY,
            font=(Fonts.FAMILY, 12, "bold")
        )
        self.badge.grid(row=0, column=0, rowspan=2, padx=Dimensions.PAD_MD, pady=Dimensions.PAD_MD, sticky="n")
        
        # 2. Main Title (Action)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=(Fonts.FAMILY, Fonts.SIZE_BASE, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
            justify="left"
        )
        self.title_label.grid(row=0, column=1, sticky="ew", padx=(0, Dimensions.PAD_MD), pady=(Dimensions.PAD_MD, 0))
        
        # 3. Reasoning (Why this step?)
        if reasoning:
            self.reasoning_label = ctk.CTkLabel(
                self,
                text=f"💡 {reasoning}",
                font=(Fonts.FAMILY, Fonts.SIZE_SM, "italic"),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
                justify="left",
                wraplength=280
            )
            self.reasoning_label.grid(row=1, column=1, sticky="ew", padx=(0, Dimensions.PAD_MD), pady=(2, Dimensions.PAD_MD))
        else:
            # Add padding if no reasoning
            self.title_label.grid_configure(pady=Dimensions.PAD_MD)
        
        # 4. Status Icon (Right side)
        self.status_icon = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI Emoji", 18),
            width=30
        )
        self.status_icon.grid(row=0, column=2, rowspan=2, padx=Dimensions.PAD_MD, pady=Dimensions.PAD_MD)
    
    def set_status(self, status: StepStatus):
        """Update visual status of step"""
        self._status = status
        
        if status == StepStatus.PENDING:
            self.configure(border_color=Colors.BORDER)
            self.badge.configure(fg_color=Colors.BG_HOVER)
            self.status_icon.configure(text="", text_color=Colors.TEXT_DISABLED)
            self.title_label.configure(text_color=Colors.TEXT_SECONDARY)
            
        elif status == StepStatus.RUNNING:
            self.configure(border_color=Colors.ACCENT_PRIMARY)
            self.badge.configure(fg_color=Colors.ACCENT_PRIMARY)
            self.status_icon.configure(text="⏳", text_color=Colors.ACCENT_PRIMARY)
            self.title_label.configure(text_color=Colors.TEXT_PRIMARY)
            
        elif status == StepStatus.COMPLETED:
            self.configure(border_color=Colors.ACCENT_SUCCESS)
            self.badge.configure(fg_color=Colors.ACCENT_SUCCESS)
            self.status_icon.configure(text="✅", text_color=Colors.ACCENT_SUCCESS)
            self.title_label.configure(text_color=Colors.TEXT_SECONDARY)
            
        elif status == StepStatus.FAILED:
            self.configure(border_color=Colors.ACCENT_ERROR)
            self.badge.configure(fg_color=Colors.ACCENT_ERROR)
            self.status_icon.configure(text="❌", text_color=Colors.ACCENT_ERROR)
            self.title_label.configure(text_color=Colors.ACCENT_ERROR)


class PlanViewer(ctk.CTkFrame):
    """
    Container for Plan display with Planner-Navigator architecture.
    Shows high-level goals from Planner, not low-level Navigator actions.
    """
    
    def __init__(
        self, 
        master,
        on_pause: Callable[[], None] = None,
        on_resume: Callable[[], None] = None,
        **kwargs
    ):
        super().__init__(
            master, 
            fg_color=Colors.BG_SECONDARY,
            corner_radius=Dimensions.RADIUS_MD,
            **kwargs
        )
        
        self.on_pause = on_pause
        self.on_resume = on_resume
        self._steps: List[PlanStepItem] = []
        self._current_step_index = -1
        self._is_paused = False
        
        self._create_layout()
    
    def _create_layout(self):
        """Create main layout with header, scrollable steps, and control buttons"""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_SM)
        
        ctk.CTkLabel(
            header,
            text="📋 Execution Plan",
            font=Fonts.subheading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        # Steps count badge
        self.steps_count = ctk.CTkLabel(
            header,
            text="0 steps",
            font=Fonts.small(),
            text_color=Colors.TEXT_SECONDARY
        )
        self.steps_count.pack(side="right")
        
        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=Dimensions.PAD_SM, pady=Dimensions.PAD_SM)
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No plan yet.\nSend a task to see the execution steps.",
            font=Fonts.body(),
            text_color=Colors.TEXT_SECONDARY,
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=Dimensions.PAD_2XL)
        
        # Control buttons (Pause/Resume)
        self.controls_frame = ctk.CTkFrame(self, fg_color=Colors.BG_TERTIARY, height=50)
        self.controls_frame.pack(fill="x", side="bottom")
        self.controls_frame.pack_propagate(False)
        
        self.pause_btn = ctk.CTkButton(
            self.controls_frame,
            text="⏸️ Pause",
            width=100,
            height=35,
            fg_color=Colors.ACCENT_WARNING,
            hover_color="#D97706",
            text_color="#ffffff",
            corner_radius=Dimensions.RADIUS_SM,
            command=self._toggle_pause
        )
        self.pause_btn.pack(side="left", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_SM)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.controls_frame,
            text="",
            font=Fonts.small(),
            text_color=Colors.TEXT_SECONDARY
        )
        self.progress_label.pack(side="right", padx=Dimensions.PAD_MD)
        
        # Hide controls initially
        self.controls_frame.pack_forget()
    
    def render_plan(self, plan_json: List[Dict]):
        """
        Render the full plan from Planner output.
        
        Args:
            plan_json: List of step dicts with keys:
                - step (int): Step number
                - action (str): Main action/goal
                - reasoning (str, optional): Why this step
        """
        # Clear existing steps
        self.clear()
        
        if not plan_json:
            return
        
        # Hide empty state
        self.empty_label.pack_forget()
        
        # Create step widgets
        for item in plan_json:
            step_widget = PlanStepItem(
                self.scroll_frame,
                step_number=item.get("step", len(self._steps) + 1),
                title=item.get("action", ""),
                reasoning=item.get("reasoning", "")
            )
            step_widget.pack(fill="x", pady=Dimensions.PAD_XS)
            self._steps.append(step_widget)
        
        # Update header
        self.steps_count.configure(text=f"{len(self._steps)} steps")
        
        # Show controls
        self.controls_frame.pack(fill="x", side="bottom")
        self._update_progress()
    
    def update_current_step(self, step_index: int, status: StepStatus):
        """
        Update status of a specific step (0-indexed).
        
        Args:
            step_index: 0-based index of step
            status: New status to set
        """
        if 0 <= step_index < len(self._steps):
            self._steps[step_index].set_status(status)
            
            if status == StepStatus.RUNNING:
                self._current_step_index = step_index
            
            self._update_progress()
    
    def start_step(self, step_index: int):
        """Mark a step as running"""
        self.update_current_step(step_index, StepStatus.RUNNING)
    
    def complete_step(self, step_index: int):
        """Mark a step as completed"""
        self.update_current_step(step_index, StepStatus.COMPLETED)
    
    def fail_step(self, step_index: int):
        """Mark a step as failed"""
        self.update_current_step(step_index, StepStatus.FAILED)
    
    def _update_progress(self):
        """Update progress label"""
        if not self._steps:
            self.progress_label.configure(text="")
            return
        
        completed = sum(1 for s in self._steps if s._status == StepStatus.COMPLETED)
        total = len(self._steps)
        self.progress_label.configure(text=f"Progress: {completed}/{total}")
    
    def _toggle_pause(self):
        """Toggle pause/resume state"""
        self._is_paused = not self._is_paused
        
        if self._is_paused:
            self.pause_btn.configure(text="▶️ Resume", fg_color=Colors.ACCENT_SUCCESS, hover_color="#16A34A")
            if self.on_pause:
                self.on_pause()
        else:
            self.pause_btn.configure(text="⏸️ Pause", fg_color=Colors.ACCENT_WARNING, hover_color="#D97706")
            if self.on_resume:
                self.on_resume()
    
    def clear(self):
        """Clear all steps"""
        for step in self._steps:
            step.destroy()
        self._steps.clear()
        self._current_step_index = -1
        self._is_paused = False
        
        # Show empty state
        self.empty_label.pack(expand=True, pady=Dimensions.PAD_2XL)
        
        # Hide controls
        self.controls_frame.pack_forget()
        
        # Reset header
        self.steps_count.configure(text="0 steps")
        self.pause_btn.configure(text="⏸️ Pause", fg_color=Colors.ACCENT_WARNING)
    
    # Legacy API compatibility
    def add_step(self, description: str, tool_name: str = "", status: StepStatus = StepStatus.PENDING) -> int:
        """Legacy method - add single step dynamically"""
        self.empty_label.pack_forget()
        
        step_number = len(self._steps) + 1
        step_widget = PlanStepItem(
            self.scroll_frame,
            step_number=step_number,
            title=description,
            reasoning=tool_name if tool_name else ""
        )
        step_widget.set_status(status)
        step_widget.pack(fill="x", pady=Dimensions.PAD_XS)
        self._steps.append(step_widget)
        
        self.steps_count.configure(text=f"{len(self._steps)} steps")
        self.controls_frame.pack(fill="x", side="bottom")
        
        # Scroll to bottom
        self.scroll_frame._parent_canvas.yview_moveto(1.0)
        
        return step_number
    
    def update_step_status(self, step_number: int, status: StepStatus):
        """Legacy method - update step by 1-based number"""
        self.update_current_step(step_number - 1, status)

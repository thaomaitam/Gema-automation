"""
General Tab Component
General settings matching Nanobrowser's design
"""
import customtkinter as ctk
from typing import Dict, Any, Callable

from gui.styles import Colors, Fonts, Dimensions, Styles
from gui.config import GENERAL_CONFIG


class SettingRow(ctk.CTkFrame):
    """Individual setting row with label + control"""
    
    def __init__(
        self, 
        parent,
        label: str,
        description: str = "",
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Label column
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            font=Fonts.body(),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                label_frame,
                text=description,
                font=Fonts.caption(),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
                wraplength=350
            ).pack(anchor="w")
        
        # Control area (to be filled by child)
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.pack(side="right", padx=Dimensions.PAD_MD)


class NumberSetting(SettingRow):
    """Number input setting"""
    
    def __init__(
        self, 
        parent,
        label: str,
        description: str = "",
        value: int = 0,
        min_val: int = 0,
        max_val: int = 100,
        **kwargs
    ):
        super().__init__(parent, label, description, **kwargs)
        
        self.min_val = min_val
        self.max_val = max_val
        
        self.var = ctk.StringVar(value=str(value))
        self.entry = ctk.CTkEntry(
            self.control_frame,
            textvariable=self.var,
            width=Dimensions.NUMBER_INPUT_WIDTH,
            height=36,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=Dimensions.RADIUS_SM,
            text_color=Colors.TEXT_PRIMARY,
            justify="center"
        )
        self.entry.pack()
    
    def get_value(self) -> int:
        try:
            val = int(self.var.get())
            return max(self.min_val, min(self.max_val, val))
        except ValueError:
            return self.min_val
    
    def set_value(self, value: int):
        self.var.set(str(value))


class ToggleSetting(SettingRow):
    """Toggle/Switch setting"""
    
    def __init__(
        self, 
        parent,
        label: str,
        description: str = "",
        value: bool = False,
        **kwargs
    ):
        super().__init__(parent, label, description, **kwargs)
        
        self.var = ctk.BooleanVar(value=value)
        self.switch = ctk.CTkSwitch(
            self.control_frame,
            text="",
            variable=self.var,
            button_color=Colors.TOGGLE_ON,
            progress_color=Colors.TOGGLE_ON,
            fg_color=Colors.TOGGLE_OFF,
            button_hover_color=Colors.ACCENT_SUCCESS,
            width=44
        )
        self.switch.pack()
    
    def get_value(self) -> bool:
        return self.var.get()
    
    def set_value(self, value: bool):
        self.var.set(value)


class GeneralTab(ctk.CTkScrollableFrame):
    """General settings tab matching Nanobrowser design"""
    
    def __init__(self, parent, config: Dict[str, Any] = None, **kwargs):
        super().__init__(
            parent, 
            fg_color=Colors.BG_PRIMARY,
            corner_radius=0,
            **kwargs
        )
        
        self.config = config or GENERAL_CONFIG.copy()
        self._settings: Dict[str, Any] = {}
        
        self._create_settings()
    
    def _create_settings(self):
        """Create all settings"""
        # Header
        ctk.CTkLabel(
            self,
            text="General",
            font=Fonts.heading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", padx=Dimensions.PAD_LG, pady=(Dimensions.PAD_LG, Dimensions.PAD_MD))
        
        # Settings container
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        # Max Steps per Task
        self._settings["max_steps"] = NumberSetting(
            settings_frame,
            label="Max Steps per Task",
            description="Step limit per task",
            value=self.config.get("max_steps", 20),
            min_val=1,
            max_val=100
        )
        self._settings["max_steps"].pack(fill="x", pady=Dimensions.PAD_MD)
        
        self._add_divider(settings_frame)
        
        # Max Actions per Step
        self._settings["max_actions_per_step"] = NumberSetting(
            settings_frame,
            label="Max Actions per Step",
            description="Action limit per step",
            value=self.config.get("max_actions_per_step", 5),
            min_val=1,
            max_val=20
        )
        self._settings["max_actions_per_step"].pack(fill="x", pady=Dimensions.PAD_MD)
        
        self._add_divider(settings_frame)
        
        # Failure Tolerance
        self._settings["failure_tolerance"] = NumberSetting(
            settings_frame,
            label="Failure Tolerance",
            description="How many consecutive failures before stopping",
            value=self.config.get("failure_tolerance", 3),
            min_val=1,
            max_val=10
        )
        self._settings["failure_tolerance"].pack(fill="x", pady=Dimensions.PAD_MD)
        
        self._add_divider(settings_frame)
        
        # Enable Vision
        self._settings["vision_enabled"] = ToggleSetting(
            settings_frame,
            label="Enable Vision",
            description="Use vision capability of LLMs (consumes more tokens for better results)",
            value=self.config.get("vision_enabled", True)
        )
        self._settings["vision_enabled"].pack(fill="x", pady=Dimensions.PAD_MD)
        
        self._add_divider(settings_frame)
        
        # Display Highlights
        self._settings["highlight_actions"] = ToggleSetting(
            settings_frame,
            label="Display Highlights",
            description="Show visual highlights on interactive elements (e.g. buttons, links, etc.)",
            value=self.config.get("highlight_actions", True)
        )
        self._settings["highlight_actions"].pack(fill="x", pady=Dimensions.PAD_MD)
        
        self._add_divider(settings_frame)
        
        # Replanning Frequency
        self._settings["replanning_frequency"] = NumberSetting(
            settings_frame,
            label="Replanning Frequency",
            description="Reconsider and update the plan every [Number] steps",
            value=self.config.get("replanning_frequency", 3),
            min_val=1,
            max_val=20
        )
        self._settings["replanning_frequency"].pack(fill="x", pady=Dimensions.PAD_MD)
        
        self._add_divider(settings_frame)
        
        # App Load Wait Time
        self._settings["app_wait_time_ms"] = NumberSetting(
            settings_frame,
            label="App Load Wait Time",
            description="Minimum wait time after app loads (250-5000ms)",
            value=self.config.get("app_wait_time_ms", 2000),
            min_val=250,
            max_val=5000
        )
        self._settings["app_wait_time_ms"].pack(fill="x", pady=Dimensions.PAD_MD)
    
    def _add_divider(self, parent):
        """Add a horizontal divider"""
        ctk.CTkFrame(
            parent,
            fg_color=Colors.DIVIDER,
            height=1
        ).pack(fill="x", pady=Dimensions.PAD_SM)
    
    def get_values(self) -> Dict[str, Any]:
        """Get all settings values"""
        return {
            "max_steps": self._settings["max_steps"].get_value(),
            "max_actions_per_step": self._settings["max_actions_per_step"].get_value(),
            "failure_tolerance": self._settings["failure_tolerance"].get_value(),
            "vision_enabled": self._settings["vision_enabled"].get_value(),
            "highlight_actions": self._settings["highlight_actions"].get_value(),
            "replanning_frequency": self._settings["replanning_frequency"].get_value(),
            "app_wait_time_ms": self._settings["app_wait_time_ms"].get_value(),
        }
    
    def set_values(self, config: Dict[str, Any]):
        """Set all settings values"""
        for key, widget in self._settings.items():
            if key in config:
                widget.set_value(config[key])

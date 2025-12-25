"""
Settings Modal Component (Refactored)
Professional settings modal with sidebar navigation
Only 2 tabs: General and Models (with integrated providers/prompts)
"""
import customtkinter as ctk
from typing import Dict, Any, Callable

from gui.styles import Colors, Fonts, Dimensions, Styles
from gui.settings.general_tab import GeneralTab
from gui.settings.models_tab import ModelsTab
from gui.config import GENERAL_CONFIG, PLANNER_CONFIG, NAVIGATOR_CONFIG
from gui.storage.config_storage import ConfigStorage


class SidebarButton(ctk.CTkButton):
    """Sidebar navigation button"""
    
    def __init__(self, parent, text: str, icon: str, is_active: bool = False, **kwargs):
        super().__init__(
            parent,
            text=f"{icon}  {text}",
            anchor="w",
            height=40,
            corner_radius=Dimensions.RADIUS_SM,
            **kwargs
        )
        self.set_active(is_active)
    
    def set_active(self, is_active: bool):
        """Set button active/inactive state"""
        if is_active:
            self.configure(
                fg_color=Colors.ACCENT_PRIMARY,
                hover_color=Colors.ACCENT_PRIMARY,
                text_color="#ffffff"
            )
        else:
            self.configure(
                fg_color="transparent",
                hover_color=Colors.BG_HOVER,
                text_color=Colors.TEXT_SECONDARY
            )


class SettingsModal(ctk.CTkToplevel):
    """Professional settings modal with sidebar navigation"""
    
    def __init__(
        self, 
        parent,
        config: Dict[str, Any] = None,
        on_save: Callable[[Dict[str, Any]], None] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.config = config or {
            "general": GENERAL_CONFIG.copy(),
            "planner": PLANNER_CONFIG.copy(),
            "navigator": NAVIGATOR_CONFIG.copy(),
            "providers": []
        }
        self.on_save = on_save
        self._active_tab = "general"
        
        self._setup_window()
        self._create_layout()
    
    def _setup_window(self):
        """Configure window properties"""
        self.title("Settings")
        self.geometry(f"{Dimensions.SETTINGS_WIDTH}x{Dimensions.SETTINGS_HEIGHT}")
        self.resizable(False, False)
        
        # Modal behavior
        self.transient(self.master)
        self.grab_set()
        
        # Center on parent
        self.after(10, self._center_on_parent)
        
        # Dark theme
        self.configure(fg_color=Colors.BG_PRIMARY)
    
    def _center_on_parent(self):
        """Center window on parent"""
        self.update_idletasks()
        parent = self.master
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _create_layout(self):
        """Create modal layout"""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Sidebar
        self._create_sidebar(container)
        
        # Content area
        self._create_content_area(container)
        
        # Footer with buttons
        self._create_footer()
    
    def _create_sidebar(self, parent):
        """Create sidebar with navigation"""
        sidebar = ctk.CTkFrame(
            parent, 
            fg_color=Colors.BG_SECONDARY,
            width=Dimensions.SETTINGS_SIDEBAR_WIDTH,
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Header
        ctk.CTkLabel(
            sidebar,
            text="Settings",
            font=Fonts.subheading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(padx=Dimensions.PAD_LG, pady=Dimensions.PAD_LG, anchor="w")
        
        # Navigation buttons (only 2 tabs now)
        self.nav_buttons: Dict[str, SidebarButton] = {}
        
        self.nav_buttons["general"] = SidebarButton(
            sidebar,
            text="General",
            icon="⚙️",
            is_active=True,
            command=lambda: self._switch_tab("general")
        )
        self.nav_buttons["general"].pack(fill="x", padx=Dimensions.PAD_SM, pady=Dimensions.PAD_XS)
        
        self.nav_buttons["models"] = SidebarButton(
            sidebar,
            text="Models",
            icon="🧠",
            is_active=False,
            command=lambda: self._switch_tab("models")
        )
        self.nav_buttons["models"].pack(fill="x", padx=Dimensions.PAD_SM, pady=Dimensions.PAD_XS)
    
    def _create_content_area(self, parent):
        """Create main content area"""
        self.content_area = ctk.CTkFrame(parent, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Create tabs
        self.tabs: Dict[str, ctk.CTkFrame] = {}
        
        # General tab
        self.tabs["general"] = GeneralTab(
            self.content_area,
            config=self.config.get("general", {})
        )
        self.tabs["general"].pack(fill="both", expand=True)
        
        # Models tab (with integrated providers and prompts)
        self.tabs["models"] = ModelsTab(
            self.content_area,
            planner_config=self.config.get("planner", {}),
            navigator_config=self.config.get("navigator", {}),
            providers=self.config.get("providers", [])
        )
    
    def _create_footer(self):
        """Create footer with action buttons"""
        footer = ctk.CTkFrame(self, fg_color=Colors.BG_SECONDARY, height=60)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)
        
        # Buttons container
        btn_container = ctk.CTkFrame(footer, fg_color="transparent")
        btn_container.pack(side="right", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
        
        # Cancel button
        ctk.CTkButton(
            btn_container,
            text="Cancel",
            command=self.destroy,
            **Styles.secondary_button(),
            width=80
        ).pack(side="left", padx=Dimensions.PAD_XS)
        
        # Save button
        ctk.CTkButton(
            btn_container,
            text="Save",
            command=self._save,
            **Styles.primary_button(),
            width=80
        ).pack(side="left", padx=Dimensions.PAD_XS)
    
    def _switch_tab(self, tab_name: str):
        """Switch to a different tab"""
        if tab_name == self._active_tab:
            return
        
        # Update navigation buttons
        for name, btn in self.nav_buttons.items():
            btn.set_active(name == tab_name)
        
        # Hide current tab
        self.tabs[self._active_tab].pack_forget()
        
        # Show new tab
        self.tabs[tab_name].pack(fill="both", expand=True)
        
        self._active_tab = tab_name
    
    def _save(self):
        """Save settings and close modal"""
        # Collect all settings from Models tab (includes providers and role configs)
        models_values = self.tabs["models"].get_values()
        
        config = {
            "general": self.tabs["general"].get_values(),
            "planner": models_values.get("planner", {}),
            "navigator": models_values.get("navigator", {}),
            "providers": models_values.get("providers", [])
        }
        
        # Persist to storage
        storage = ConfigStorage()
        storage.save(config)
        
        if self.on_save:
            self.on_save(config)
        
        self.destroy()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration without closing"""
        models_values = self.tabs["models"].get_values()
        return {
            "general": self.tabs["general"].get_values(),
            "planner": models_values.get("planner", {}),
            "navigator": models_values.get("navigator", {}),
            "providers": models_values.get("providers", [])
        }

"""
Device Panel Component
Manages device selection and refresh
"""
import customtkinter as ctk
import threading
from typing import List, Dict, Any, Callable

from gui.styles import Colors, Fonts, Dimensions, Styles
from tools import TOOL_REGISTRY


class DevicePanel(ctk.CTkFrame):
    """Device management panel with device dropdown and refresh button"""
    
    def __init__(
        self, 
        parent, 
        on_device_change: Callable[[str], None] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color=Colors.BG_TERTIARY, corner_radius=Dimensions.RADIUS_MD, **kwargs)
        
        self.on_device_change = on_device_change
        self._devices: List[Dict[str, Any]] = []
        
        self._create_widgets()
        self.refresh_devices()
    
    def _create_widgets(self):
        """Build panel UI"""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=Dimensions.PAD_MD, pady=(Dimensions.PAD_MD, Dimensions.PAD_SM))
        
        ctk.CTkLabel(
            header, 
            text="📱 Device",
            font=Fonts.subheading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            width=30,
            height=30,
            corner_radius=Dimensions.RADIUS_SM,
            fg_color="transparent",
            hover_color=Colors.BG_HOVER,
            command=self.refresh_devices
        )
        self.refresh_btn.pack(side="right")
        
        # Device dropdown
        self.device_var = ctk.StringVar(value="Loading...")
        self.device_menu = ctk.CTkOptionMenu(
            self,
            variable=self.device_var,
            values=["Loading..."],
            command=self._on_selection_change,
            **Styles.dropdown()
        )
        self.device_menu.pack(fill="x", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_SM)
        
        # Device info label
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=Fonts.caption(),
            text_color=Colors.TEXT_SECONDARY
        )
        self.info_label.pack(padx=Dimensions.PAD_MD, pady=(0, Dimensions.PAD_MD))
    
    def refresh_devices(self):
        """Refresh device list from ADB"""
        self.refresh_btn.configure(state="disabled")
        self.device_var.set("Scanning...")
        
        def load():
            try:
                result = TOOL_REGISTRY["list_emulators"]()
                if result.get("success"):
                    devices = result.get("devices", [])
                    names = [d.get("name", d.get("id", "Unknown")) for d in devices]
                    if names:
                        self.after(0, lambda: self._update_devices(names, devices))
                    else:
                        self.after(0, lambda: self._update_devices(["No devices found"], []))
                else:
                    self.after(0, lambda: self._update_devices(["Error: ADB failed"], []))
            except Exception as e:
                self.after(0, lambda: self._update_devices([f"Error: {e}"], []))
            finally:
                self.after(0, lambda: self.refresh_btn.configure(state="normal"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def _update_devices(self, names: List[str], devices: List[Dict[str, Any]]):
        """Update dropdown with device list"""
        self._devices = devices
        self.device_menu.configure(values=names)
        
        if names:
            self.device_var.set(names[0])
            if devices:
                info = devices[0]
                dims = info.get("dimensions", "")
                self.info_label.configure(text=dims)
            else:
                self.info_label.configure(text="")
    
    def _on_selection_change(self, value: str):
        """Handle device selection change"""
        # Update info label
        for device in self._devices:
            if device.get("name") == value or device.get("id") == value:
                self.info_label.configure(text=device.get("dimensions", ""))
                break
        
        if self.on_device_change:
            self.on_device_change(value)
    
    def get_selected_device(self) -> str:
        """Get currently selected device ID"""
        return self.device_var.get()

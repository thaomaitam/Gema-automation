"""
Gemma Android Automation - Professional GUI
Advanced interface with full AI customization
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import json
from typing import Optional
from pathlib import Path

from agent.model import GemmaAgent, list_available_models, TOOL_FUNCTIONS
from tools import TOOL_REGISTRY
import config


class SettingsWindow(ctk.CTkToplevel):
    """Advanced settings window"""
    
    def __init__(self, parent, agent: 'GemmaAgent', on_save=None):
        super().__init__(parent)
        self.agent = agent
        self.on_save = on_save
        
        self.title("⚙️ Cài đặt AI")
        self.geometry("600x700")
        self.transient(parent)
        self.grab_set()
        
        # Scrollable content
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_model_settings()
        self._create_prompt_settings()
        self._create_tool_settings()
        self._create_buttons()
    
    def _create_model_settings(self):
        """Model parameters section"""
        section = ctk.CTkFrame(self.scroll, fg_color="#2A2A2A", corner_radius=10)
        section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(section, text="🤖 Cài đặt Model", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=10)
        
        # Temperature
        temp_frame = ctk.CTkFrame(section, fg_color="transparent")
        temp_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(temp_frame, text="Temperature:", width=120).pack(side="left")
        self.temp_var = ctk.DoubleVar(value=0.7)
        self.temp_slider = ctk.CTkSlider(temp_frame, from_=0, to=2, variable=self.temp_var, width=200)
        self.temp_slider.pack(side="left", padx=10)
        self.temp_label = ctk.CTkLabel(temp_frame, text="0.7", width=40)
        self.temp_label.pack(side="left")
        self.temp_slider.configure(command=lambda v: self.temp_label.configure(text=f"{v:.1f}"))
        
        # Max tokens
        tokens_frame = ctk.CTkFrame(section, fg_color="transparent")
        tokens_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(tokens_frame, text="Max Tokens:", width=120).pack(side="left")
        self.tokens_var = ctk.StringVar(value="2048")
        ctk.CTkEntry(tokens_frame, textvariable=self.tokens_var, width=100).pack(side="left", padx=10)
        
        # Keep alive
        keep_frame = ctk.CTkFrame(section, fg_color="transparent")
        keep_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(keep_frame, text="Keep Alive:", width=120).pack(side="left")
        self.keep_var = ctk.StringVar(value="5m")
        ctk.CTkOptionMenu(keep_frame, variable=self.keep_var, values=["1m", "5m", "15m", "30m", "1h"], width=100).pack(side="left", padx=10)
    
    def _create_prompt_settings(self):
        """System prompt editor"""
        section = ctk.CTkFrame(self.scroll, fg_color="#2A2A2A", corner_radius=10)
        section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(section, text="📝 System Prompt", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=10)
        
        # Get current prompt
        current_prompt = self.agent.messages[0]["content"] if self.agent.messages else ""
        
        self.prompt_text = ctk.CTkTextbox(section, height=200, font=("Consolas", 12))
        self.prompt_text.pack(fill="x", padx=15, pady=(0, 15))
        self.prompt_text.insert("1.0", current_prompt)
    
    def _create_tool_settings(self):
        """Tool enable/disable toggles"""
        section = ctk.CTkFrame(self.scroll, fg_color="#2A2A2A", corner_radius=10)
        section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(section, text="🔧 Công cụ", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=10)
        
        self.tool_vars = {}
        tools_frame = ctk.CTkFrame(section, fg_color="transparent")
        tools_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        for i, tool_name in enumerate(TOOL_REGISTRY.keys()):
            var = ctk.BooleanVar(value=True)
            self.tool_vars[tool_name] = var
            
            row = i // 2
            col = i % 2
            
            cb = ctk.CTkCheckBox(tools_frame, text=tool_name, variable=var, width=180)
            cb.grid(row=row, column=col, sticky="w", padx=5, pady=3)
    
    def _create_buttons(self):
        """Action buttons"""
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 Lưu", command=self._save, fg_color="#2D5A27", hover_color="#3D7A37").pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Reset", command=self._reset, fg_color="#4A4A4A").pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="❌ Hủy", command=self.destroy, fg_color="#5A3A3A", hover_color="#7A4A4A").pack(side="right", padx=5)
    
    def _save(self):
        """Save settings"""
        # Update system prompt
        new_prompt = self.prompt_text.get("1.0", "end-1c")
        if self.agent.messages:
            self.agent.messages[0]["content"] = new_prompt
        
        if self.on_save:
            self.on_save({
                "temperature": self.temp_var.get(),
                "max_tokens": int(self.tokens_var.get()),
                "keep_alive": self.keep_var.get(),
                "enabled_tools": {k: v.get() for k, v in self.tool_vars.items()}
            })
        
        self.destroy()
    
    def _reset(self):
        """Reset to defaults"""
        self.temp_var.set(0.7)
        self.tokens_var.set("2048")
        self.keep_var.set("5m")
        for var in self.tool_vars.values():
            var.set(True)


class DevicePanel(ctk.CTkFrame):
    """Device management panel"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#1A1A1A", **kwargs)
        
        ctk.CTkLabel(self, text="📱 Thiết bị", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        self.device_var = ctk.StringVar(value="Chọn thiết bị...")
        self.device_menu = ctk.CTkOptionMenu(self, variable=self.device_var, values=["Đang tải..."], width=180)
        self.device_menu.pack(padx=10, pady=5)
        
        ctk.CTkButton(self, text="🔄 Làm mới", command=self.refresh_devices, height=30, fg_color="#3A3A3A").pack(padx=10, pady=5)
        
        self.device_info = ctk.CTkLabel(self, text="", font=("Segoe UI", 10), text_color="#888888")
        self.device_info.pack(pady=5)
        
        self.refresh_devices()
    
    def refresh_devices(self):
        """Refresh device list"""
        def load():
            try:
                result = TOOL_REGISTRY["list_emulators"]()
                if result.get("success"):
                    devices = result.get("devices", [])
                    names = [d.get("name", d.get("id", "Unknown")) for d in devices]
                    if names:
                        self.after(0, lambda: self._update_devices(names, devices))
                    else:
                        self.after(0, lambda: self._update_devices(["Không có thiết bị"], []))
            except Exception as e:
                self.after(0, lambda: self._update_devices([f"Lỗi: {e}"], []))
        
        threading.Thread(target=load, daemon=True).start()
    
    def _update_devices(self, names: list, devices: list):
        self.device_menu.configure(values=names)
        if names:
            self.device_var.set(names[0])
            if devices:
                info = devices[0]
                self.device_info.configure(text=f"{info.get('dimensions', 'N/A')}")


class ChatBubble(ctk.CTkFrame):
    """Enhanced chat bubble with tool execution display"""
    
    def __init__(self, parent, message: str, is_user: bool, tool_info: dict = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        bubble_color = "#2D5A27" if is_user else "#3A3A3A"
        align = "e" if is_user else "w"
        
        # Tool execution indicator
        if tool_info:
            tool_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=8)
            tool_frame.pack(anchor=align, padx=10, pady=2)
            
            icon = "✅" if tool_info.get("success") else "❌"
            ctk.CTkLabel(tool_frame, text=f"🔧 {tool_info.get('name', 'Tool')} {icon}", 
                        font=("Segoe UI", 11), text_color="#888888").pack(padx=10, pady=5)
        
        # Message bubble
        bubble = ctk.CTkFrame(self, fg_color=bubble_color, corner_radius=15)
        bubble.pack(anchor=align, padx=10, pady=2)
        
        ctk.CTkLabel(bubble, text=message, wraplength=450, justify="left", 
                    font=("Segoe UI", 13)).pack(padx=15, pady=10)


class GemmaProGUI(ctk.CTk):
    """Professional GUI with full customization"""
    
    def __init__(self):
        super().__init__()
        
        self.title("🤖 Gemma Android Automation Pro")
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.agent: Optional[GemmaAgent] = None
        self.is_processing = False
        self.settings = {"temperature": 0.7, "max_tokens": 2048}
        
        self._create_layout()
        self._load_models()
    
    def _create_layout(self):
        """Create main layout"""
        # Left sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#1A1A1A")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo
        ctk.CTkLabel(self.sidebar, text="🤖 Gemma Pro", font=("Segoe UI", 22, "bold")).pack(pady=20)
        
        # New Chat
        ctk.CTkButton(self.sidebar, text="📝 Chat mới", command=self._new_chat, height=40, 
                     fg_color="#2D5A27", hover_color="#3D7A37").pack(padx=15, pady=5, fill="x")
        
        # Model selector
        ctk.CTkLabel(self.sidebar, text="Model:", font=("Segoe UI", 12)).pack(padx=15, pady=(20, 5), anchor="w")
        
        self.model_var = ctk.StringVar(value=config.DEFAULT_MODEL)
        self.model_menu = ctk.CTkOptionMenu(self.sidebar, variable=self.model_var, 
                                           values=[config.DEFAULT_MODEL], command=self._on_model_change, width=210)
        self.model_menu.pack(padx=15, pady=5)
        
        # Device panel
        self.device_panel = DevicePanel(self.sidebar)
        self.device_panel.pack(padx=15, pady=20, fill="x")
        
        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="y", expand=True)
        
        # Bottom buttons
        ctk.CTkButton(self.sidebar, text="⚙️ Cài đặt AI", command=self._show_settings, height=35, 
                     fg_color="transparent", hover_color="#333333").pack(padx=15, pady=5, fill="x")
        ctk.CTkButton(self.sidebar, text="💾 Xuất lịch sử", command=self._export_history, height=35,
                     fg_color="transparent", hover_color="#333333").pack(padx=15, pady=5, fill="x")
        ctk.CTkButton(self.sidebar, text="🌙 Đổi theme", command=self._toggle_theme, height=35,
                     fg_color="transparent", hover_color="#333333").pack(padx=15, pady=(5, 20), fill="x")
        
        # Main chat area
        self.main = ctk.CTkFrame(self, fg_color="#252525", corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)
        
        # Chat display
        self.chat_frame = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._show_welcome()
        
        # Input area
        self._create_input_area()
    
    def _create_input_area(self):
        """Create input area with controls"""
        input_frame = ctk.CTkFrame(self.main, fg_color="#1E1E1E", height=100)
        input_frame.pack(fill="x", padx=20, pady=20)
        input_frame.pack_propagate(False)
        
        # Top row - quick actions
        actions = ctk.CTkFrame(input_frame, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(actions, text="📸 Screenshot", width=100, height=28, command=lambda: self._quick_action("take_screenshot"),
                     fg_color="#3A3A3A").pack(side="left", padx=2)
        ctk.CTkButton(actions, text="📱 Devices", width=80, height=28, command=lambda: self._quick_action("list_emulators"),
                     fg_color="#3A3A3A").pack(side="left", padx=2)
        ctk.CTkButton(actions, text="⬅️ Back", width=60, height=28, command=lambda: self._quick_action("press_back"),
                     fg_color="#3A3A3A").pack(side="left", padx=2)
        
        # Input container
        container = ctk.CTkFrame(input_frame, fg_color="#2A2A2A", corner_radius=25)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.input_entry = ctk.CTkEntry(container, placeholder_text="Nhập lệnh...", font=("Segoe UI", 14),
                                        height=45, border_width=0, fg_color="transparent")
        self.input_entry.pack(side="left", fill="both", expand=True, padx=15)
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        
        ctk.CTkLabel(container, text=config.DEFAULT_MODEL, font=("Segoe UI", 10), 
                    text_color="#666666").pack(side="right", padx=10)
        
        self.send_btn = ctk.CTkButton(container, text="↑", width=40, height=40, corner_radius=20,
                                      command=self._send_message, fg_color="#2D5A27", hover_color="#3D7A37")
        self.send_btn.pack(side="right", padx=5)
    
    def _show_welcome(self):
        """Show welcome screen"""
        frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        frame.pack(expand=True, pady=80)
        
        ctk.CTkLabel(frame, text="🦙", font=("Segoe UI Emoji", 60)).pack(pady=10)
        ctk.CTkLabel(frame, text="Gemma Android Automation Pro", font=("Segoe UI", 20, "bold")).pack(pady=5)
        ctk.CTkLabel(frame, text="Nhập lệnh hoặc dùng nút nhanh bên dưới", 
                    font=("Segoe UI", 12), text_color="#888888").pack()
    
    def _load_models(self):
        def load():
            models = list_available_models()
            if models:
                self.after(0, lambda: self._update_models(models))
        threading.Thread(target=load, daemon=True).start()
    
    def _update_models(self, models: list):
        self.model_menu.configure(values=models)
        if config.DEFAULT_MODEL in models:
            self.model_var.set(config.DEFAULT_MODEL)
        elif models:
            self.model_var.set(models[0])
        self._init_agent()
    
    def _init_agent(self):
        try:
            self.agent = GemmaAgent(model=self.model_var.get())
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi tạo agent: {e}")
    
    def _on_model_change(self, model: str):
        self._init_agent()
    
    def _new_chat(self):
        if self.agent:
            self.agent.reset()
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        self._show_welcome()
    
    def _quick_action(self, action: str):
        """Execute quick action"""
        if action == "take_screenshot":
            self._send_with_text("Chụp màn hình")
        elif action == "list_emulators":
            self._send_with_text("Liệt kê các thiết bị đã kết nối")
        elif action == "press_back":
            self._send_with_text("Nhấn nút back")
    
    def _send_with_text(self, text: str):
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, text)
        self._send_message()
    
    def _send_message(self):
        if self.is_processing:
            return
        
        message = self.input_entry.get().strip()
        if not message or not self.agent:
            return
        
        # Clear welcome
        if len(self.chat_frame.winfo_children()) == 1:
            for w in self.chat_frame.winfo_children():
                w.destroy()
        
        self._add_message(message, is_user=True)
        self.input_entry.delete(0, "end")
        
        self.is_processing = True
        self.send_btn.configure(state="disabled")
        
        def process():
            try:
                response = self.agent.chat(message, verbose=True)
                self.after(0, lambda r=response: self._add_message(r, is_user=False))
            except Exception as ex:
                err = f"Lỗi: {ex}"
                self.after(0, lambda e=err: self._add_message(e, is_user=False))
            finally:
                self.after(0, self._finish_processing)
        
        threading.Thread(target=process, daemon=True).start()
    
    def _finish_processing(self):
        self.is_processing = False
        self.send_btn.configure(state="normal")
    
    def _add_message(self, message: str, is_user: bool, tool_info: dict = None):
        bubble = ChatBubble(self.chat_frame, message, is_user, tool_info)
        bubble.pack(fill="x", pady=2)
        self.chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _show_settings(self):
        if self.agent:
            SettingsWindow(self, self.agent, on_save=self._apply_settings)
    
    def _apply_settings(self, settings: dict):
        self.settings = settings
    
    def _export_history(self):
        if not self.agent or not self.agent.messages:
            messagebox.showinfo("Thông báo", "Không có lịch sử để xuất")
            return
        
        file = filedialog.asksaveasfilename(defaultextension=".json", 
                                           filetypes=[("JSON", "*.json"), ("Text", "*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.agent.messages, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", f"Đã lưu vào {file}")
    
    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)


def main():
    app = GemmaProGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

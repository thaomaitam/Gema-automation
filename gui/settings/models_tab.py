"""
Models Tab Component (Refactored)
Unified LLM Providers + Model Selection + Role-Specific Prompts

Features:
- Custom providers from saved config (dynamic)
- Provider selector per role (Planner/Navigator)
- Model dropdown based on selected provider's models
- System prompt editor per role
"""
import customtkinter as ctk
from typing import Dict, Any, List, Callable
import re

from gui.styles import Colors, Fonts, Dimensions, Styles


# Default prompts
DEFAULT_PLANNER_PROMPT = """Bạn là AI Planner. Nhiệm vụ của bạn là phân tích yêu cầu và tạo kế hoạch thực hiện.

## Quy trình
1. Phân tích yêu cầu người dùng
2. Xác định các bước cần thực hiện
3. Đề xuất tool phù hợp cho từng bước
4. Trả về plan dưới dạng JSON

## Output Format
{
  "goal": "Mục tiêu chính",
  "steps": [
    {"step": 1, "action": "Mô tả hành động", "tool_hint": "tool_name"},
    ...
  ]
}
"""

DEFAULT_NAVIGATOR_PROMPT = """Bạn là Android Automation Navigator. Bạn THỰC THI các bước automation qua uiautomator2.

## TOOLS CHI TIẾT
- `app_start(package_name="...")` - Mở ứng dụng
- `click_element(text="..." OR resource_id="...")` - Click element
- `set_element_text(text="...", input_text="nội dung")` - Nhập text
- `press(x=123, y=456)` - Tap tọa độ
- `press_back()` - Nút Back
- `swipe(start_x, start_y, end_x, end_y)` - Vuốt
- `get_ui_elements_info()` - Lấy danh sách UI elements
- `take_screenshot()` - Chụp màn hình

## QUY TẮC
1. Thực hiện ĐÚNG 1 bước được yêu cầu
2. ƯU TIÊN dùng `text` thay vì `resource_id`
3. Trả lời ngắn gọn
"""


class ProviderFormCard(ctk.CTkFrame):
    """Form for adding/editing a custom LLM provider - inline display."""
    
    def __init__(
        self, 
        parent,
        provider_data: Dict[str, Any] = None,
        on_save: Callable[[Dict[str, Any]], None] = None,
        on_delete: Callable[[str], None] = None,
        is_new: bool = False,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.BG_TERTIARY,
            border_color=Colors.BORDER if not is_new else Colors.ACCENT_PRIMARY,
            border_width=1,
            corner_radius=Dimensions.RADIUS_MD,
            **kwargs
        )
        
        self.provider_data = provider_data or {}
        self.on_save = on_save
        self.on_delete = on_delete
        self.is_new = is_new
        self._show_password = False
        self._expanded = is_new  # Expand if new
        
        self._create_ui()
    
    def _create_ui(self):
        """Build provider card UI."""
        # Header row (always visible)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
        
        name = self.provider_data.get("name", "New Provider")
        self.name_label = ctk.CTkLabel(
            header,
            text=f"🔌 {name}" if not self.is_new else "➕ Add New Provider",
            font=(Fonts.FAMILY, Fonts.SIZE_BASE, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        self.name_label.pack(side="left")
        
        # Status/buttons
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        if not self.is_new:
            # Connected status
            if self.provider_data.get("api_key"):
                ctk.CTkLabel(
                    btn_frame,
                    text="● Connected",
                    font=Fonts.small(),
                    text_color=Colors.ACCENT_SUCCESS
                ).pack(side="left", padx=Dimensions.PAD_SM)
            
            # Expand/collapse button
            self.toggle_btn = ctk.CTkButton(
                btn_frame,
                text="▼" if not self._expanded else "▲",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=Colors.BG_HOVER,
                command=self._toggle_expand
            )
            self.toggle_btn.pack(side="left")
            
            # Delete button
            ctk.CTkButton(
                btn_frame,
                text="🗑️",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=Colors.ACCENT_ERROR,
                command=lambda: self.on_delete(self.provider_data["name"]) if self.on_delete else None
            ).pack(side="left")
        
        # Expandable form
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        if self._expanded:
            self.form_frame.pack(fill="x", padx=Dimensions.PAD_LG, pady=(0, Dimensions.PAD_MD))
            self._create_form_fields()
    
    def _toggle_expand(self):
        """Toggle form expansion."""
        self._expanded = not self._expanded
        self.toggle_btn.configure(text="▲" if self._expanded else "▼")
        
        if self._expanded:
            self.form_frame.pack(fill="x", padx=Dimensions.PAD_LG, pady=(0, Dimensions.PAD_MD))
            self._create_form_fields()
        else:
            for widget in self.form_frame.winfo_children():
                widget.destroy()
            self.form_frame.pack_forget()
    
    def _create_form_fields(self):
        """Create form input fields."""
        # Name
        name_row = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        name_row.pack(fill="x", pady=Dimensions.PAD_XS)
        
        ctk.CTkLabel(name_row, text="Name", width=80, font=Fonts.body(),
                    text_color=Colors.TEXT_SECONDARY).pack(side="left")
        
        self.name_entry = ctk.CTkEntry(
            name_row, placeholder_text="Provider name",
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            border_width=1, corner_radius=Dimensions.RADIUS_SM,
            text_color=Colors.TEXT_PRIMARY, height=36
        )
        self.name_entry.pack(side="left", fill="x", expand=True)
        if self.provider_data.get("name"):
            self.name_entry.insert(0, self.provider_data["name"])
        
        # API Key
        key_row = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        key_row.pack(fill="x", pady=Dimensions.PAD_XS)
        
        ctk.CTkLabel(key_row, text="API Key", width=80, font=Fonts.body(),
                    text_color=Colors.TEXT_SECONDARY).pack(side="left")
        
        self.key_entry = ctk.CTkEntry(
            key_row, placeholder_text="API Key (optional)", show="•",
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            border_width=1, corner_radius=Dimensions.RADIUS_SM,
            text_color=Colors.TEXT_PRIMARY, height=36
        )
        self.key_entry.pack(side="left", fill="x", expand=True)
        if self.provider_data.get("api_key"):
            self.key_entry.insert(0, self.provider_data["api_key"])
        
        # Base URL
        url_row = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        url_row.pack(fill="x", pady=Dimensions.PAD_XS)
        
        ctk.CTkLabel(url_row, text="Base URL*", width=80, font=Fonts.body(),
                    text_color=Colors.TEXT_SECONDARY).pack(side="left")
        
        self.url_entry = ctk.CTkEntry(
            url_row, placeholder_text="http://localhost:8317/v1",
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            border_width=1, corner_radius=Dimensions.RADIUS_SM,
            text_color=Colors.TEXT_PRIMARY, height=36
        )
        self.url_entry.pack(side="left", fill="x", expand=True)
        if self.provider_data.get("base_url"):
            self.url_entry.insert(0, self.provider_data["base_url"])
        
        # Models
        models_row = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        models_row.pack(fill="x", pady=Dimensions.PAD_XS)
        
        ctk.CTkLabel(models_row, text="Models", width=80, font=Fonts.body(),
                    text_color=Colors.TEXT_SECONDARY).pack(side="left")
        
        self.models_entry = ctk.CTkEntry(
            models_row, placeholder_text="model1, model2, model3",
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            border_width=1, corner_radius=Dimensions.RADIUS_SM,
            text_color=Colors.TEXT_PRIMARY, height=36
        )
        self.models_entry.pack(side="left", fill="x", expand=True)
        models = self.provider_data.get("models", [])
        if models:
            self.models_entry.insert(0, ", ".join(models))
        
        ctk.CTkLabel(self.form_frame, text="Comma-separated model names",
                    font=Fonts.small(), text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, Dimensions.PAD_SM))
        
        # Save button
        ctk.CTkButton(
            self.form_frame,
            text="💾 Save Provider",
            height=36,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color="#2563EB",
            corner_radius=Dimensions.RADIUS_SM,
            command=self._save
        ).pack(fill="x", pady=Dimensions.PAD_SM)
    
    def _save(self):
        """Save provider data."""
        name = self.name_entry.get().strip()
        if not name:
            return
        name = re.sub(r'\s+', '-', name)
        
        base_url = self.url_entry.get().strip()
        if not base_url:
            return
        
        models_text = self.models_entry.get().strip()
        models = [m.strip() for m in re.split(r'[,\s]+', models_text) if m.strip()]
        
        provider = {
            "name": name,
            "api_key": self.key_entry.get().strip(),
            "base_url": base_url,
            "models": models
        }
        
        if self.on_save:
            self.on_save(provider)


class RoleConfigCard(ctk.CTkFrame):
    """Configuration card for a role (Planner or Navigator)."""
    
    def __init__(
        self,
        parent,
        role_name: str,
        description: str,
        config: Dict[str, Any],
        providers: List[Dict[str, Any]],
        default_prompt: str,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.BG_TERTIARY,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=Dimensions.RADIUS_MD,
            **kwargs
        )
        
        self.role_name = role_name
        self.config = config.copy()
        self.providers = providers
        self.default_prompt = default_prompt
        self._prompt_expanded = False
        
        self._create_card(role_name, description)
    
    def _create_card(self, role_name: str, description: str):
        """Build role card UI."""
        # Header
        ctk.CTkLabel(
            self, text=role_name,
            font=(Fonts.FAMILY, Fonts.SIZE_LG, "bold"),
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", padx=Dimensions.PAD_LG, pady=(Dimensions.PAD_LG, 0))
        
        ctk.CTkLabel(
            self, text=description,
            font=Fonts.small(), text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", padx=Dimensions.PAD_LG, pady=(Dimensions.PAD_XS, Dimensions.PAD_MD))
        
        # Provider selector
        provider_row = ctk.CTkFrame(self, fg_color="transparent")
        provider_row.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        ctk.CTkLabel(provider_row, text="Provider", width=80, font=Fonts.body(),
                    text_color=Colors.TEXT_SECONDARY).pack(side="left")
        
        provider_names = [p["name"] for p in self.providers if p.get("name")]
        if not provider_names:
            provider_names = ["(No providers)"]
        
        current_provider = self.config.get("provider", provider_names[0] if provider_names else "")
        self.provider_var = ctk.StringVar(value=current_provider)
        self.provider_dropdown = ctk.CTkOptionMenu(
            provider_row,
            variable=self.provider_var,
            values=provider_names,
            fg_color=Colors.BG_INPUT,
            button_color=Colors.BG_HOVER,
            button_hover_color=Colors.BG_HOVER,
            dropdown_fg_color=Colors.BG_TERTIARY,
            dropdown_hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Dimensions.RADIUS_SM,
            command=self._on_provider_change
        )
        self.provider_dropdown.pack(side="left", fill="x", expand=True)
        
        # Model selector
        model_row = ctk.CTkFrame(self, fg_color="transparent")
        model_row.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        ctk.CTkLabel(model_row, text="Model", width=80, font=Fonts.body(),
                    text_color=Colors.TEXT_SECONDARY).pack(side="left")
        
        models = self._get_models_for_provider(current_provider)
        current_model = self.config.get("model", models[0] if models else "")
        self.model_var = ctk.StringVar(value=current_model)
        self.model_dropdown = ctk.CTkOptionMenu(
            model_row,
            variable=self.model_var,
            values=models if models else ["(No models)"],
            fg_color=Colors.BG_INPUT,
            button_color=Colors.BG_HOVER,
            button_hover_color=Colors.BG_HOVER,
            dropdown_fg_color=Colors.BG_TERTIARY,
            dropdown_hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Dimensions.RADIUS_SM
        )
        self.model_dropdown.pack(side="left", fill="x", expand=True)
        
        # Prompt toggle button
        prompt_row = ctk.CTkFrame(self, fg_color="transparent")
        prompt_row.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        self.prompt_toggle_btn = ctk.CTkButton(
            prompt_row,
            text="📝 System Prompt ▼",
            height=32,
            fg_color=Colors.BG_INPUT,
            hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_SECONDARY,
            corner_radius=Dimensions.RADIUS_SM,
            command=self._toggle_prompt
        )
        self.prompt_toggle_btn.pack(fill="x")
        
        # Prompt editor (hidden initially)
        self.prompt_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        # Bottom padding
        ctk.CTkFrame(self, fg_color="transparent", height=Dimensions.PAD_SM).pack()
    
    def _get_models_for_provider(self, provider_name: str) -> List[str]:
        """Get models for a specific provider."""
        for p in self.providers:
            if p.get("name") == provider_name:
                return p.get("models", [])
        return []
    
    def _on_provider_change(self, new_provider: str):
        """Handle provider change - update model dropdown."""
        models = self._get_models_for_provider(new_provider)
        if models:
            self.model_dropdown.configure(values=models)
            self.model_var.set(models[0])
        else:
            self.model_dropdown.configure(values=["(No models)"])
            self.model_var.set("(No models)")
    
    def _toggle_prompt(self):
        """Toggle prompt editor visibility."""
        self._prompt_expanded = not self._prompt_expanded
        
        if self._prompt_expanded:
            self.prompt_toggle_btn.configure(text="📝 System Prompt ▲")
            self.prompt_frame.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
            
            # Create prompt editor
            self.prompt_text = ctk.CTkTextbox(
                self.prompt_frame,
                font=Fonts.small(),
                fg_color=Colors.BG_INPUT,
                text_color=Colors.TEXT_PRIMARY,
                border_color=Colors.BORDER,
                border_width=1,
                corner_radius=Dimensions.RADIUS_SM,
                height=150,
                wrap="word"
            )
            self.prompt_text.pack(fill="x", pady=Dimensions.PAD_XS)
            
            # Load current or default prompt
            current = self.config.get("system_prompt") or self.default_prompt
            self.prompt_text.insert("1.0", current)
            
            # Reset button
            ctk.CTkButton(
                self.prompt_frame,
                text="↺ Reset to Default",
                height=28,
                fg_color=Colors.BG_HOVER,
                hover_color=Colors.BG_INPUT,
                text_color=Colors.TEXT_SECONDARY,
                corner_radius=Dimensions.RADIUS_SM,
                command=self._reset_prompt
            ).pack(anchor="e", pady=Dimensions.PAD_XS)
        else:
            self.prompt_toggle_btn.configure(text="📝 System Prompt ▼")
            for widget in self.prompt_frame.winfo_children():
                widget.destroy()
            self.prompt_frame.pack_forget()
    
    def _reset_prompt(self):
        """Reset prompt to default."""
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", self.default_prompt)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        config = {
            "provider": self.provider_var.get(),
            "model": self.model_var.get(),
        }
        
        # Get prompt if expanded
        if self._prompt_expanded and hasattr(self, 'prompt_text'):
            prompt = self.prompt_text.get("1.0", "end-1c").strip()
            if prompt != self.default_prompt.strip():
                config["system_prompt"] = prompt
        elif self.config.get("system_prompt"):
            config["system_prompt"] = self.config["system_prompt"]
        
        return config
    
    def update_providers(self, providers: List[Dict[str, Any]]):
        """Update available providers."""
        self.providers = providers
        provider_names = [p["name"] for p in providers if p.get("name")]
        if provider_names:
            self.provider_dropdown.configure(values=provider_names)


class ModelsTab(ctk.CTkScrollableFrame):
    """Unified Models configuration tab with integrated Providers."""
    
    def __init__(
        self, 
        parent, 
        planner_config: Dict[str, Any] = None,
        navigator_config: Dict[str, Any] = None,
        providers: List[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            parent, 
            fg_color=Colors.BG_PRIMARY,
            corner_radius=0,
            **kwargs
        )
        
        self.planner_config = planner_config or {}
        self.navigator_config = navigator_config or {}
        self.providers = providers or []
        
        self._create_content()
    
    def _create_content(self):
        """Create tab content."""
        # Section 1: LLM Providers
        ctk.CTkLabel(
            self, text="LLM Providers",
            font=Fonts.heading(), text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", padx=Dimensions.PAD_LG, pady=(Dimensions.PAD_LG, Dimensions.PAD_MD))
        
        ctk.CTkLabel(
            self, text="Add your API providers here. Models will appear in role selection below.",
            font=Fonts.small(), text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", padx=Dimensions.PAD_LG, pady=(0, Dimensions.PAD_MD))
        
        # Provider cards container
        self.providers_container = ctk.CTkFrame(self, fg_color="transparent")
        self.providers_container.pack(fill="x", padx=Dimensions.PAD_LG)
        
        self._render_providers()
        
        # Add New Provider button
        self.add_btn = ctk.CTkButton(
            self,
            text="+ Add New Provider",
            height=40,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color="#2563EB",
            text_color="#ffffff",
            corner_radius=Dimensions.RADIUS_SM,
            font=(Fonts.FAMILY, Fonts.SIZE_BASE, "bold"),
            command=self._add_provider
        )
        self.add_btn.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_MD)
        
        # Section 2: Model Selection
        ctk.CTkLabel(
            self, text="Model Selection",
            font=Fonts.heading(), text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", padx=Dimensions.PAD_LG, pady=(Dimensions.PAD_XL, Dimensions.PAD_MD))
        
        # Planner Card
        self.planner_card = RoleConfigCard(
            self,
            role_name="Planner",
            description="Develops strategies and plans tasks (Needs High IQ)",
            config=self.planner_config,
            providers=self.providers,
            default_prompt=DEFAULT_PLANNER_PROMPT
        )
        self.planner_card.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        # Navigator Card
        self.navigator_card = RoleConfigCard(
            self,
            role_name="Navigator",
            description="Executes actions on device (Needs Speed)",
            config=self.navigator_config,
            providers=self.providers,
            default_prompt=DEFAULT_NAVIGATOR_PROMPT
        )
        self.navigator_card.pack(fill="x", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
    
    def _render_providers(self):
        """Render provider cards."""
        for widget in self.providers_container.winfo_children():
            widget.destroy()
        
        for provider in self.providers:
            card = ProviderFormCard(
                self.providers_container,
                provider_data=provider,
                on_save=self._save_provider,
                on_delete=self._delete_provider,
                is_new=False
            )
            card.pack(fill="x", pady=Dimensions.PAD_XS)
    
    def _add_provider(self):
        """Show form for new provider."""
        # Check if already adding
        for widget in self.providers_container.winfo_children():
            if isinstance(widget, ProviderFormCard) and widget.is_new:
                return
        
        card = ProviderFormCard(
            self.providers_container,
            provider_data={},
            on_save=self._save_provider,
            on_delete=None,
            is_new=True
        )
        card.pack(fill="x", pady=Dimensions.PAD_XS)
    
    def _save_provider(self, provider: Dict[str, Any]):
        """Save provider and refresh."""
        # Remove existing with same name
        self.providers = [p for p in self.providers if p.get("name") != provider["name"]]
        self.providers.append(provider)
        
        self._render_providers()
        self._update_role_cards()
    
    def _delete_provider(self, name: str):
        """Delete provider."""
        self.providers = [p for p in self.providers if p.get("name") != name]
        self._render_providers()
        self._update_role_cards()
    
    def _update_role_cards(self):
        """Update role cards with new provider list."""
        self.planner_card.update_providers(self.providers)
        self.navigator_card.update_providers(self.providers)
    
    def get_values(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return {
            "planner": self.planner_card.get_config(),
            "navigator": self.navigator_card.get_config(),
            "providers": self.providers
        }
    
    def set_providers(self, providers: List[Dict[str, Any]]):
        """Set providers list."""
        self.providers = providers or []
        self._render_providers()
        self._update_role_cards()

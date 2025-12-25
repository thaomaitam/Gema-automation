"""
Gema Cloud Automation - Professional GUI
Entry Point with Split View 70/30 Layout (Nanobrowser Style)
Implements Planner-Navigator Architecture
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloud Agent imports
from agent.brain import CloudAgent, Brain
from agent.adapters import CLIProxyBrain
from agent.planner import PlannerBrain

# GUI imports
from gui.styles import Colors, Fonts, Dimensions, Styles
from gui.config import GENERAL_CONFIG, PLANNER_CONFIG, NAVIGATOR_CONFIG
from gui.components import AgentPanel, WorkspacePanel
from gui.components.agent_panel import AgentStatus
from gui.components.plan_viewer import StepStatus
from gui.settings import SettingsModal
from gui.storage import ConfigStorage, HistoryStorage
from tools import TOOL_REGISTRY


class GemaCloudGUI(ctk.CTk):
    """Main Gema Cloud GUI Application with Planner-Navigator Architecture"""
    
    def __init__(self):
        super().__init__()
        
        self.title("☁️ Gema Cloud Automation")
        self.geometry("1280x800")
        self.minsize(1024, 700)
        
        # Apply dark theme
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Colors.BG_PRIMARY)
        
        # Brains State (Planner-Navigator)
        self.planner: Optional[PlannerBrain] = None
        self.navigator: Optional[Brain] = None
        self.agent: Optional[CloudAgent] = None
        
        # Execution State
        self._current_plan: List[Dict] = []
        self._current_step_index: int = 0
        self._is_paused: bool = False
        self._is_executing: bool = False
        
        # Storage
        self.config_storage = ConfigStorage()
        self.history_storage = HistoryStorage()
        self._current_session_id = None
        
        # Config - load from persistent storage
        self.config = self.config_storage.load()
        
        self._create_layout()
        self._init_agents()
    
    def _create_layout(self):
        """Create Split View 70/30 layout like Nanobrowser"""
        # Header
        self._create_header()
        
        # Main content frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=Dimensions.PAD_MD, pady=(0, Dimensions.PAD_MD))
        
        # Configure grid for 70/30 split
        main_frame.grid_columnconfigure(0, weight=7)  # Left: 70%
        main_frame.grid_columnconfigure(1, weight=3)  # Right: 30%
        main_frame.grid_rowconfigure(0, weight=1)
        
        # LEFT PANEL: Workspace (70%)
        self.workspace_panel = WorkspacePanel(main_frame)
        self.workspace_panel.grid(
            row=0, column=0, 
            padx=(0, Dimensions.PAD_SM), 
            pady=0, 
            sticky="nsew"
        )
        
        # RIGHT PANEL: Agent Panel (30%)
        self.agent_panel = AgentPanel(main_frame, on_send=self._handle_message)
        self.agent_panel.grid(
            row=0, column=1, 
            padx=(Dimensions.PAD_SM, 0), 
            pady=0, 
            sticky="nsew"
        )
    
    def _create_header(self):
        """Create header with logo and controls"""
        header = ctk.CTkFrame(self, fg_color=Colors.BG_SECONDARY, height=55)
        header.pack(fill="x", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_MD)
        header.pack_propagate(False)
        
        # Logo
        ctk.CTkLabel(
            header,
            text="☁️ Gema Cloud",
            font=Fonts.heading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        # Status badge
        self.status_badge = ctk.CTkLabel(
            header,
            text="● Connected",
            font=Fonts.small(),
            text_color=Colors.ACCENT_SUCCESS
        )
        self.status_badge.pack(side="left", padx=Dimensions.PAD_MD)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            header,
            text="⚙️ Settings",
            width=100,
            height=35,
            corner_radius=Dimensions.RADIUS_SM,
            fg_color=Colors.BG_TERTIARY,
            hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            command=self._show_settings
        )
        settings_btn.pack(side="right", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_SM)
        
        # New Chat button
        ctk.CTkButton(
            header,
            text="📝 New Chat",
            width=100,
            height=35,
            fg_color=Colors.ACCENT_SUCCESS,
            hover_color="#1EA34F",
            text_color="#ffffff",
            corner_radius=Dimensions.RADIUS_SM,
            command=self._new_chat
        ).pack(side="right", padx=Dimensions.PAD_XS, pady=Dimensions.PAD_SM)
    
    def _init_agents(self):
        """Initialize Planner and Navigator brains"""
        try:
            # Get providers from config
            providers = self.config.get("providers", [])
            
            # 1. Initialize Planner (high-capability model)
            planner_config = self.config.get("planner", PLANNER_CONFIG)
            planner_model = planner_config.get("model", "gemini-2.5-pro")
            planner_provider_name = planner_config.get("provider", "")
            planner_prompt = planner_config.get("system_prompt")
            
            # Find provider details
            planner_provider = self._get_provider_by_name(providers, planner_provider_name)
            planner_api_key = planner_provider.get("api_key") if planner_provider else os.getenv("CLIPROXY_API_KEY", "gemaauto")
            planner_base_url = planner_provider.get("base_url", "http://localhost:8317/v1") if planner_provider else "http://localhost:8317/v1"
            
            if not planner_api_key:
                self.agent_panel.add_message(
                    "⚠️ No API Key found for Planner. Please configure in Settings.",
                    is_user=False
                )
                self.status_badge.configure(text="● No API Key", text_color=Colors.ACCENT_WARNING)
                return
            
            self.planner = PlannerBrain(
                api_key=planner_api_key,
                model_name=planner_model
            )
            
            # 2. Initialize Navigator (fast model with tool callback)
            nav_config = self.config.get("navigator", NAVIGATOR_CONFIG)
            nav_model = nav_config.get("model", "gemini-2.5-flash")
            nav_provider_name = nav_config.get("provider", "")
            nav_prompt = nav_config.get("system_prompt")  # Per-role system prompt
            
            # Find provider details
            nav_provider = self._get_provider_by_name(providers, nav_provider_name)
            nav_api_key = nav_provider.get("api_key") if nav_provider else os.getenv("CLIPROXY_API_KEY", "gemaauto")
            nav_base_url = nav_provider.get("base_url", "http://localhost:8317/v1") if nav_provider else "http://localhost:8317/v1"
            
            self.navigator = CLIProxyBrain(
                api_key=nav_api_key,
                model_name=nav_model,
                base_url=nav_base_url,
                tool_callback=self._on_tool_event,
                system_prompt=nav_prompt  # Pass per-role prompt
            )
            
            # Apply Caching Middleware to Navigator
            from agent.middleware.cache_manager import CacheManager
            from agent.middleware.caching_brain import CachingBrain
            
            cache_manager = CacheManager()
            self.navigator = CachingBrain(self.navigator, cache_manager, user_id="default_user")
            
            # Initialize Agent with Navigator
            self.agent = CloudAgent(self.navigator)
            
            print(f"🧠 Planner: {planner_model} ({planner_provider_name})")
            print(f"🚀 Navigator: {nav_model} ({nav_provider_name})")
            
            self.status_badge.configure(text=f"● {nav_model}", text_color=Colors.ACCENT_SUCCESS)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.agent_panel.add_message(f"❌ Error: {e}", is_user=False)
            self.status_badge.configure(text="● Error", text_color=Colors.ACCENT_ERROR)
    
    def _get_provider_by_name(self, providers: List[Dict], name: str) -> Optional[Dict]:
        """Find a provider by name from the providers list."""
        for p in providers:
            if p.get("name") == name:
                return p
        return None
    
    def _on_tool_event(self, event: str, data: dict):
        """Handle tool execution events from Brain - update PlanViewer"""
        tool_name = data.get("name", "")
        tool_args = data.get("args", {})
        
        # Build description from tool name and args
        args_str = ", ".join(f'{k}="{v}"' for k, v in list(tool_args.items())[:2])
        description = f"{tool_name}({args_str})" if args_str else tool_name
        
        if event == "tool_start":
            # Add step and mark as running
            from gui.components.plan_viewer import StepStatus
            step_id = self.after(0, lambda: self._add_plan_step(description, tool_name))
        elif event == "tool_done":
            # Mark last step as done
            self.after(0, lambda: self._update_last_step_status("done"))
        elif event == "tool_failed":
            # Mark last step as failed
            self.after(0, lambda: self._update_last_step_status("failed"))
    
    def _add_plan_step(self, description: str, tool_name: str):
        """Add a step to the plan viewer (must be called from main thread)"""
        from gui.components.plan_viewer import StepStatus
        step_id = self.agent_panel.plan_view.add_step(description, tool_name, StepStatus.RUNNING)
        self._current_step_id = step_id
    
    def _update_last_step_status(self, status: str):
        """Update the last step's status (must be called from main thread)"""
        from gui.components.plan_viewer import StepStatus
        if hasattr(self, '_current_step_id') and self._current_step_id:
            status_enum = StepStatus.COMPLETED if status == "done" else StepStatus.FAILED
            self.agent_panel.plan_view.update_step_status(self._current_step_id, status_enum)
    
    def _handle_message(self, message: str, attached_files: List[Path] = None):
        """Handle user message with Planner-Navigator workflow"""
        attached_files = attached_files or []
        
        if not self.planner or not self.agent:
            self.agent_panel.add_message("⚠️ Agent not initialized. Check Settings.", is_user=False)
            return
        
        # Create session if needed
        if not self._current_session_id:
            title = message[:50] + "..." if len(message) > 50 else message
            self._current_session_id = self.history_storage.create_session(title)
        
        # Save to history
        file_paths = [str(f) for f in attached_files]
        self.history_storage.add_message(self._current_session_id, "user", message, file_paths)
        
        # Display files info if any
        display_msg = message
        if attached_files:
            files_str = ", ".join([f.name for f in attached_files[:3]])
            if len(attached_files) > 3:
                files_str += f" (+{len(attached_files) - 3} more)"
            display_msg = f"{message}\n📎 {files_str}"
        
        # Add user message
        self.agent_panel.add_message(display_msg, is_user=True)
        self.agent_panel.set_processing(True)
        self.agent_panel.set_status(AgentStatus.PLANNING)
        
        # Clear previous plan and switch to Plan tab
        self.agent_panel.clear_plan()
        self.agent_panel._switch_tab("plan")
        
        def execute_plan():
            try:
                # ========================================
                # PHASE 1: PLANNING
                # ========================================
                print("🧠 Phase 1: Planning...")
                
                # Take initial screenshot
                screenshot_path = None
                try:
                    result = TOOL_REGISTRY["take_screenshot"]()
                    if result.get("success"):
                        screenshot_path = result.get("filepath")
                        if screenshot_path:
                            self.after(0, lambda p=screenshot_path: self.workspace_panel.display_screenshot(p))
                except Exception as e:
                    print(f"Screenshot failed: {e}")
                
                # Call Planner to generate plan
                plan_result = self.planner.create_plan(
                    user_request=message,
                    screenshot_path=screenshot_path
                )
                
                if "error" in plan_result and plan_result["error"]:
                    self.after(0, lambda: self.agent_panel.add_message(
                        f"⚠️ Planning failed: {plan_result.get('error', 'Unknown error')}", 
                        is_user=False
                    ))
                    return
                
                # Extract steps from plan
                steps = plan_result.get("steps", [])
                goal = plan_result.get("goal", message)
                
                if not steps:
                    # Fallback to single-step if no plan generated
                    steps = [{"step": 1, "action": message, "reasoning": "Direct execution"}]
                
                # Display plan in PlanViewer
                self.after(0, lambda: self._render_plan(steps))
                print(f"📋 Plan: {len(steps)} steps")
                
                # Store plan for execution
                self._current_plan = steps
                self._current_step_index = 0
                
                # Brief pause to show plan before execution
                time.sleep(0.5)
                
                # ========================================
                # PHASE 2: NAVIGATION (Execute each step)
                # ========================================
                print("🚀 Phase 2: Navigating...")
                self.after(0, lambda: self.agent_panel.set_status(AgentStatus.NAVIGATING))
                
                for idx, step in enumerate(steps):
                    if self._is_paused:
                        print("⏸️ Execution paused")
                        break
                    
                    step_action = step.get("action", "")
                    step_tool = step.get("tool_hint", "")
                    
                    print(f"  Step {idx + 1}: {step_action}")
                    
                    # Mark step as running
                    self.after(0, lambda i=idx: self.agent_panel.plan_view.start_step(i))
                    
                    # Take fresh screenshot before each step
                    try:
                        result = TOOL_REGISTRY["take_screenshot"]()
                        if result.get("success"):
                            screenshot_path = result.get("filepath")
                            if screenshot_path:
                                self.after(0, lambda p=screenshot_path: self.workspace_panel.display_screenshot(p))
                    except Exception:
                        pass
                    
                    # Navigate this step using the Navigator agent
                    navigator_prompt = f"""Thực hiện bước sau: {step_action}
                    
Gợi ý tool: {step_tool}

Hãy thực hiện CHÍNH XÁC hành động này, không làm gì khác."""
                    
                    try:
                        response = self.agent.chat(
                            navigator_prompt,
                            verbose=True,
                            screenshot_path=screenshot_path
                        )
                        
                        # Mark step as completed
                        self.after(0, lambda i=idx: self.agent_panel.plan_view.complete_step(i))
                        
                    except Exception as step_error:
                        print(f"  ❌ Step failed: {step_error}")
                        self.after(0, lambda i=idx: self.agent_panel.plan_view.fail_step(i))
                        break
                    
                    # Brief pause between steps
                    time.sleep(0.3)
                
                # ========================================
                # PHASE 3: COMPLETION
                # ========================================
                # Take final screenshot
                try:
                    result = TOOL_REGISTRY["take_screenshot"]()
                    if result.get("success"):
                        final_path = result.get("filepath")
                        if final_path:
                            self.after(0, lambda p=final_path: self.workspace_panel.display_screenshot(p))
                except Exception:
                    pass
                
                # Show completion message
                self.after(0, lambda: self.agent_panel.add_message(
                    f"✅ Completed: {goal}",
                    is_user=False
                ))
                
            except Exception as ex:
                import traceback
                traceback.print_exc()
                self.after(0, lambda e=str(ex): self.agent_panel.add_message(f"❌ Error: {e}", is_user=False))
            finally:
                self.after(0, lambda: self.agent_panel.set_processing(False))
                self.after(0, lambda: self.agent_panel.set_status(AgentStatus.IDLE))
        
        threading.Thread(target=execute_plan, daemon=True).start()
    
    def _render_plan(self, steps: List[Dict]):
        """Render the plan in PlanViewer"""
        self.agent_panel.plan_view.render_plan(steps)
    
    def _on_pause(self):
        """Handle pause button"""
        self._is_paused = True
        print("⏸️ Execution paused by user")
    
    def _on_resume(self):
        """Handle resume button"""
        self._is_paused = False
        print("▶️ Execution resumed")
    
    def _new_chat(self):
        """Start new chat"""
        if self.agent:
            self.agent.reset()
        self._current_plan = []
        self._current_step_index = 0
        self._is_paused = False
        self.agent_panel.clear_chat()
        self.agent_panel.clear_plan()
        self.workspace_panel.clear()
    
    def _show_settings(self):
        """Show settings modal"""
        SettingsModal(
            self,
            config=self.config,
            on_save=self._apply_settings
        )
    
    def _apply_settings(self, config: Dict[str, Any]):
        """Apply saved settings"""
        self.config = config
        self._init_agents()


def main():
    app = GemaCloudGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

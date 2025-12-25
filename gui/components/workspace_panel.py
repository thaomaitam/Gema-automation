"""
Workspace Panel Component
Left panel for displaying screenshots, task data, or live monitoring
"""
import customtkinter as ctk
from typing import Optional, Callable
from PIL import Image
import os

from gui.styles import Colors, Fonts, Dimensions


class WorkspacePanel(ctk.CTkFrame):
    """Workspace panel for displaying visual content (screenshots, task data)"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, 
            fg_color=Colors.BG_WORKSPACE,
            corner_radius=Dimensions.RADIUS_MD,
            **kwargs
        )
        
        self._current_image_path: Optional[str] = None
        self._create_layout()
    
    def _create_layout(self):
        """Create workspace layout"""
        # Header
        header = ctk.CTkFrame(self, fg_color=Colors.BG_TERTIARY, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📷 Workspace",
            font=Fonts.subheading(),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left", padx=Dimensions.PAD_LG, pady=Dimensions.PAD_SM)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            width=30,
            height=30,
            corner_radius=Dimensions.RADIUS_SM,
            fg_color="transparent",
            hover_color=Colors.BG_HOVER,
            command=self._on_refresh
        )
        self.refresh_btn.pack(side="right", padx=Dimensions.PAD_MD, pady=Dimensions.PAD_XS)
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=Dimensions.PAD_SM, pady=Dimensions.PAD_SM)
        
        # Placeholder/Welcome state
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder when no content"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        placeholder = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            placeholder,
            text="📱",
            font=("Segoe UI Emoji", 48),
            text_color=Colors.TEXT_SECONDARY
        ).pack(pady=Dimensions.PAD_SM)
        
        ctk.CTkLabel(
            placeholder,
            text="Waiting for Screenshot...",
            font=Fonts.subheading(),
            text_color=Colors.TEXT_SECONDARY
        ).pack()
        
        ctk.CTkLabel(
            placeholder,
            text="Send a command to see the device screen",
            font=Fonts.body(),
            text_color=Colors.TEXT_DISABLED
        ).pack(pady=Dimensions.PAD_XS)
    
    def display_screenshot(self, image_path: str):
        """Display a screenshot from file path"""
        # Convert to absolute path if relative
        if not os.path.isabs(image_path):
            image_path = os.path.join(os.getcwd(), image_path)
        
        if not os.path.exists(image_path):
            print(f"Screenshot not found: {image_path}")
            return
        
        self._current_image_path = image_path
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        try:
            # Load and display image
            img = Image.open(image_path)
            
            # Calculate size to fit in frame while maintaining aspect ratio
            frame_width = self.content_frame.winfo_width() or 600
            frame_height = self.content_frame.winfo_height() or 800
            
            # Scale to fit
            img_ratio = img.width / img.height
            frame_ratio = frame_width / frame_height
            
            if img_ratio > frame_ratio:
                # Image is wider, fit by width
                new_width = int(frame_width * 0.95)
                new_height = int(new_width / img_ratio)
            else:
                # Image is taller, fit by height
                new_height = int(frame_height * 0.95)
                new_width = int(new_height * img_ratio)
            
            # Create CTk image
            ctk_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(new_width, new_height)
            )
            
            # Display image
            img_label = ctk.CTkLabel(
                self.content_frame,
                image=ctk_image,
                text=""
            )
            img_label.pack(expand=True, fill="both")
            
            # Keep reference to prevent garbage collection
            img_label.image = ctk_image
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self._show_error(str(e))
    
    def _show_error(self, message: str):
        """Show error message"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        error_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        error_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            error_frame,
            text="❌",
            font=("Segoe UI Emoji", 32),
            text_color=Colors.ACCENT_ERROR
        ).pack()
        
        ctk.CTkLabel(
            error_frame,
            text="Error loading screenshot",
            font=Fonts.subheading(),
            text_color=Colors.ACCENT_ERROR
        ).pack(pady=Dimensions.PAD_XS)
        
        ctk.CTkLabel(
            error_frame,
            text=message,
            font=Fonts.small(),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=300
        ).pack()
    
    def _on_refresh(self):
        """Refresh current screenshot"""
        if self._current_image_path:
            self.display_screenshot(self._current_image_path)
    
    def display_text(self, title: str, content: str):
        """Display text content (for logs, XML, etc.)"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Text display with scrollbar
        text_box = ctk.CTkTextbox(
            self.content_frame,
            font=Fonts.mono(),
            fg_color=Colors.BG_TERTIARY,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=Dimensions.RADIUS_SM
        )
        text_box.pack(fill="both", expand=True, padx=Dimensions.PAD_SM, pady=Dimensions.PAD_SM)
        text_box.insert("1.0", content)
        text_box.configure(state="disabled")
    
    def clear(self):
        """Clear and show placeholder"""
        self._current_image_path = None
        self._show_placeholder()

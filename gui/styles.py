"""
Gema Cloud GUI - Shared Styles & Theme Constants
Professional dark theme inspired by Nanobrowser
"""

# ============================================================
# Color Palette
# ============================================================

class Colors:
    """Centralized color definitions for consistent theming"""
    
    # Background colors (Nanobrowser Dark Theme)
    BG_PRIMARY = "#0F1117"      # Deep Blue-Black background
    BG_SECONDARY = "#1E232F"    # Lighter panel background
    BG_TERTIARY = "#282D3E"     # Cards/sections
    BG_INPUT = "#323848"        # Input fields
    BG_HOVER = "#3D4455"        # Hover state
    BG_WORKSPACE = "#000000"    # Workspace/Device area
    
    # Accent colors (Nanobrowser Blue)
    ACCENT_PRIMARY = "#3B82F6"  # Nanobrowser Blue
    ACCENT_SUCCESS = "#22C55E"  # Green - success/active
    ACCENT_WARNING = "#F59E0B"  # Orange - warnings
    ACCENT_ERROR = "#EF4444"    # Red - errors/delete
    
    # Text colors (Higher Contrast)
    TEXT_PRIMARY = "#E0E4F0"    # High contrast main text
    TEXT_SECONDARY = "#949BB0"  # Brighter subtitle text
    TEXT_DISABLED = "#5A6070"   # Disabled state
    
    # Border/Divider
    BORDER = "#3b4261"
    DIVIDER = "#292e42"
    
    # Status colors
    STATUS_IDLE = "#565f89"
    STATUS_PLANNING = "#bb9af7"  # Purple
    STATUS_NAVIGATING = "#7aa2f7"  # Blue
    STATUS_RUNNING = "#9ece6a"   # Green
    
    # Toggle colors
    TOGGLE_ON = "#9ece6a"
    TOGGLE_OFF = "#414868"


# ============================================================
# Typography
# ============================================================

class Fonts:
    """Font configurations"""
    
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    # Font sizes (Increased for readability)
    SIZE_XS = 11
    SIZE_SM = 12
    SIZE_BASE = 14
    SIZE_LG = 15
    SIZE_XL = 18
    SIZE_2XL = 22
    SIZE_3XL = 28
    
    # Presets
    @staticmethod
    def heading():
        return (Fonts.FAMILY, Fonts.SIZE_2XL, "bold")
    
    @staticmethod
    def subheading():
        return (Fonts.FAMILY, Fonts.SIZE_LG, "bold")
    
    @staticmethod
    def body():
        return (Fonts.FAMILY, Fonts.SIZE_BASE)
    
    @staticmethod
    def small():
        return (Fonts.FAMILY, Fonts.SIZE_SM)
    
    @staticmethod
    def caption():
        return (Fonts.FAMILY, Fonts.SIZE_XS)
    
    @staticmethod
    def mono():
        return (Fonts.FAMILY_MONO, Fonts.SIZE_BASE)


# ============================================================
# Dimensions & Spacing
# ============================================================

class Dimensions:
    """Layout dimensions and spacing"""
    
    # Padding
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 12
    PAD_LG = 16
    PAD_XL = 24
    PAD_2XL = 32
    
    # Border radius
    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 15
    RADIUS_FULL = 20
    
    # Component sizes
    BTN_HEIGHT_SM = 28
    BTN_HEIGHT_MD = 36
    BTN_HEIGHT_LG = 45
    
    INPUT_HEIGHT = 45
    
    # Settings modal
    SETTINGS_SIDEBAR_WIDTH = 140
    SETTINGS_WIDTH = 700
    SETTINGS_HEIGHT = 550
    
    # Widget widths
    DROPDOWN_WIDTH = 250
    NUMBER_INPUT_WIDTH = 80


# ============================================================
# Component Styles (CustomTkinter kwargs)
# ============================================================

class Styles:
    """Pre-configured style dictionaries for CTk widgets"""
    
    @staticmethod
    def card():
        """Card/section container style"""
        return {
            "fg_color": Colors.BG_TERTIARY,
            "corner_radius": Dimensions.RADIUS_MD
        }
    
    @staticmethod
    def sidebar():
        """Sidebar style"""
        return {
            "fg_color": Colors.BG_SECONDARY,
            "corner_radius": 0
        }
    
    @staticmethod
    def tab_button_active():
        """Active tab button style"""
        return {
            "fg_color": Colors.ACCENT_PRIMARY,
            "hover_color": Colors.ACCENT_PRIMARY,
            "text_color": "#ffffff",
            "corner_radius": Dimensions.RADIUS_SM,
            "height": Dimensions.BTN_HEIGHT_MD
        }
    
    @staticmethod
    def tab_button_inactive():
        """Inactive tab button style"""
        return {
            "fg_color": "transparent",
            "hover_color": Colors.BG_HOVER,
            "text_color": Colors.TEXT_SECONDARY,
            "corner_radius": Dimensions.RADIUS_SM,
            "height": Dimensions.BTN_HEIGHT_MD
        }
    
    @staticmethod
    def primary_button():
        """Primary action button style"""
        return {
            "fg_color": Colors.ACCENT_PRIMARY,
            "hover_color": "#5d8ed9",
            "text_color": "#ffffff",
            "corner_radius": Dimensions.RADIUS_SM,
            "height": Dimensions.BTN_HEIGHT_MD
        }
    
    @staticmethod
    def secondary_button():
        """Secondary button style"""
        return {
            "fg_color": Colors.BG_INPUT,
            "hover_color": Colors.BG_HOVER,
            "text_color": Colors.TEXT_PRIMARY,
            "corner_radius": Dimensions.RADIUS_SM,
            "height": Dimensions.BTN_HEIGHT_MD
        }
    
    @staticmethod
    def ghost_button():
        """Ghost/transparent button style"""
        return {
            "fg_color": "transparent",
            "hover_color": Colors.BG_HOVER,
            "text_color": Colors.TEXT_PRIMARY,
            "corner_radius": Dimensions.RADIUS_SM,
            "height": Dimensions.BTN_HEIGHT_MD
        }
    
    @staticmethod
    def input_field():
        """Text input field style"""
        return {
            "fg_color": Colors.BG_INPUT,
            "border_color": Colors.BORDER,
            "border_width": 1,
            "corner_radius": Dimensions.RADIUS_SM,
            "height": Dimensions.INPUT_HEIGHT,
            "text_color": Colors.TEXT_PRIMARY
        }
    
    @staticmethod
    def dropdown():
        """Dropdown/OptionMenu style"""
        return {
            "fg_color": Colors.BG_INPUT,
            "button_color": Colors.BG_TERTIARY,
            "button_hover_color": Colors.BG_HOVER,
            "dropdown_fg_color": Colors.BG_TERTIARY,
            "dropdown_hover_color": Colors.BG_HOVER,
            "text_color": Colors.TEXT_PRIMARY,
            "corner_radius": Dimensions.RADIUS_SM,
            "width": Dimensions.DROPDOWN_WIDTH
        }
    
    @staticmethod
    def toggle():
        """Toggle/Switch style"""
        return {
            "button_color": Colors.TOGGLE_ON,
            "progress_color": Colors.TOGGLE_ON,
            "fg_color": Colors.TOGGLE_OFF,
            "button_hover_color": Colors.ACCENT_SUCCESS
        }
    
    @staticmethod
    def number_input():
        """Number input field style"""
        return {
            "fg_color": Colors.BG_INPUT,
            "border_color": Colors.BORDER,
            "border_width": 1,
            "corner_radius": Dimensions.RADIUS_SM,
            "width": Dimensions.NUMBER_INPUT_WIDTH,
            "height": 36,
            "text_color": Colors.TEXT_PRIMARY
        }

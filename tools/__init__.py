"""Tool implementations for Android automation"""
from .navigation import press, long_press, press_back, open_app, press_home
from .input import type_text, swipe, scroll_element
from .screen import take_screenshot, get_ui_elements_info
from .device_info import list_emulators, get_device_dimensions
from .recording import record_video, stop_video
from .apps import app_start, app_stop, app_clear, app_current, app_info, app_list
from .gestures import double_click, drag, pinch_in, pinch_out, swipe_points
from .system import (
    screen_on, screen_off, unlock, set_clipboard, get_clipboard,
    send_keys, clear_text, hide_keyboard, get_orientation, set_orientation,
    open_notification, open_quick_settings, get_toast, shell
)
from .elements import (
    click_element, long_click_element, get_element_info, wait_element,
    wait_element_gone, set_element_text, scroll_to_element, xpath_click, xpath_get_text
)

# Tool registry for agent executor
TOOL_REGISTRY = {
    # Navigation
    "press": press,
    "long_press": long_press,
    "press_back": press_back,
    "press_home": press_home,
    "open_app": open_app,
    
    # Input
    "type_text": type_text,
    "swipe": swipe,
    "scroll_element": scroll_element,
    
    # Screen
    "take_screenshot": take_screenshot,
    "get_ui_elements_info": get_ui_elements_info,
    
    # Device Info
    "list_emulators": list_emulators,
    "get_device_dimensions": get_device_dimensions,
    
    # Recording
    "record_video": record_video,
    "stop_video": stop_video,
    
    # App Management
    "app_start": app_start,
    "app_stop": app_stop,
    "app_clear": app_clear,
    "app_current": app_current,
    "app_info": app_info,
    "app_list": app_list,
    
    # Gestures
    "double_click": double_click,
    "drag": drag,
    "pinch_in": pinch_in,
    "pinch_out": pinch_out,
    "swipe_points": swipe_points,
    
    # System
    "screen_on": screen_on,
    "screen_off": screen_off,
    "unlock": unlock,
    "set_clipboard": set_clipboard,
    "get_clipboard": get_clipboard,
    "send_keys": send_keys,
    "clear_text": clear_text,
    "hide_keyboard": hide_keyboard,
    "get_orientation": get_orientation,
    "set_orientation": set_orientation,
    "open_notification": open_notification,
    "open_quick_settings": open_quick_settings,
    "get_toast": get_toast,
    "shell": shell,
    
    # Elements
    "click_element": click_element,
    "long_click_element": long_click_element,
    "get_element_info": get_element_info,
    "wait_element": wait_element,
    "wait_element_gone": wait_element_gone,
    "set_element_text": set_element_text,
    "scroll_to_element": scroll_to_element,
    "xpath_click": xpath_click,
    "xpath_get_text": xpath_get_text,
}

__all__ = list(TOOL_REGISTRY.keys()) + ['TOOL_REGISTRY']

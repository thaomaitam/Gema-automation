"""
System Tools - Device system interactions
"""
from typing import Optional
import subprocess

from core.device import get_device_connection, DeviceConnectionError


def screen_on(device_id: str = None) -> dict:
    """
    Turn on the screen.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.screen_on()
        
        return {"success": True, "message": "Screen turned on"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def screen_off(device_id: str = None) -> dict:
    """
    Turn off the screen.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.screen_off()
        
        return {"success": True, "message": "Screen turned off"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def unlock(device_id: str = None) -> dict:
    """
    Unlock the device screen (wake + swipe up).
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.unlock()
        
        return {"success": True, "message": "Device unlocked"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_clipboard(text: str, device_id: str = None) -> dict:
    """
    Set clipboard content.
    
    Args:
        text: Text to copy to clipboard
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.clipboard = text
        
        return {"success": True, "message": f"Copied to clipboard: {text[:50]}..."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_clipboard(device_id: str = None) -> dict:
    """
    Get clipboard content.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with clipboard text
    """
    try:
        device = get_device_connection(device_id)
        text = device.clipboard
        
        return {"success": True, "text": text, "message": f"Clipboard: {text[:50] if text else 'empty'}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_keys(text: str, clear: bool = False, device_id: str = None) -> dict:
    """
    Send text using input method (faster than type_text for some apps).
    
    Args:
        text: Text to input
        clear: If True, clear existing text first
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.send_keys(text, clear=clear)
        
        return {"success": True, "message": f"Sent keys: {text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def clear_text(device_id: str = None) -> dict:
    """
    Clear all text in the currently focused input field.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.clear_text()
        
        return {"success": True, "message": "Cleared text in input field"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def hide_keyboard(device_id: str = None) -> dict:
    """
    Hide the soft keyboard.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.hide_keyboard()
        
        return {"success": True, "message": "Keyboard hidden"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_orientation(device_id: str = None) -> dict:
    """
    Get current screen orientation.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with orientation info
    """
    try:
        device = get_device_connection(device_id)
        orientation = device.orientation
        
        return {"success": True, "orientation": orientation, "message": f"Orientation: {orientation}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_orientation(orientation: str, device_id: str = None) -> dict:
    """
    Set screen orientation.
    
    Args:
        orientation: 'natural', 'left', 'right', or 'n', 'l', 'r'
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.set_orientation(orientation)
        
        return {"success": True, "message": f"Orientation set to {orientation}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_notification(device_id: str = None) -> dict:
    """
    Open the notification panel.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.open_notification()
        
        return {"success": True, "message": "Notification panel opened"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_quick_settings(device_id: str = None) -> dict:
    """
    Open quick settings panel.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.open_quick_settings()
        
        return {"success": True, "message": "Quick settings opened"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_toast(timeout: float = 5.0, device_id: str = None) -> dict:
    """
    Get the last toast message.
    
    Args:
        timeout: Wait timeout in seconds
        device_id: Optional device ID
        
    Returns:
        dict with toast message
    """
    try:
        device = get_device_connection(device_id)
        message = device.toast.get_message(wait_timeout=timeout, default=None)
        
        return {"success": True, "message": message or "No toast message", "toast": message}
    except Exception as e:
        return {"success": False, "error": str(e)}


def shell(command: str, device_id: str = None) -> dict:
    """
    Execute a shell command on the device.
    
    Args:
        command: Shell command to execute
        device_id: Optional device ID
        
    Returns:
        dict with command output
    """
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', command])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            "success": True,
            "output": result.stdout.strip(),
            "error_output": result.stderr.strip() if result.stderr else None,
            "message": f"Command executed: {command[:50]}..."
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

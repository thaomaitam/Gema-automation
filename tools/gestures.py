"""
Gestures Tools - Advanced touch interactions
"""
from typing import Optional, List, Tuple

from core.device import get_device_connection, DeviceConnectionError


def double_click(x: int, y: int, device_id: str = None, duration: float = 0.1) -> dict:
    """
    Double click at coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        device_id: Optional device ID
        duration: Duration between clicks (default 0.1s)
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.double_click(x, y, duration)
        
        return {
            "success": True,
            "message": f"Double clicked at ({x}, {y})",
            "x": x, "y": y
        }
    except Exception as e:
        return {"success": False, "error": str(e), "x": x, "y": y}


def drag(sx: int, sy: int, ex: int, ey: int, device_id: str = None, duration: float = 0.5) -> dict:
    """
    Drag from one point to another.
    
    Args:
        sx: Start X coordinate
        sy: Start Y coordinate
        ex: End X coordinate
        ey: End Y coordinate
        device_id: Optional device ID
        duration: Drag duration in seconds (default 0.5)
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.drag(sx, sy, ex, ey, duration)
        
        return {
            "success": True,
            "message": f"Dragged from ({sx},{sy}) to ({ex},{ey})",
            "start": (sx, sy), "end": (ex, ey)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def pinch_in(x: int = None, y: int = None, percent: int = 50, device_id: str = None) -> dict:
    """
    Pinch in gesture (zoom out) at center or specified point.
    
    Args:
        x: Optional X coordinate (default center)
        y: Optional Y coordinate (default center)
        percent: Pinch percentage (default 50)
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        if x is not None and y is not None:
            device(focused=True).pinch_in(percent=percent, steps=10)
        else:
            # Pinch at screen center
            w, h = device.window_size()
            device(focused=True).pinch_in(percent=percent, steps=10)
        
        return {
            "success": True,
            "message": f"Pinch in gesture completed"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def pinch_out(x: int = None, y: int = None, percent: int = 50, device_id: str = None) -> dict:
    """
    Pinch out gesture (zoom in) at center or specified point.
    
    Args:
        x: Optional X coordinate (default center)
        y: Optional Y coordinate (default center)
        percent: Pinch percentage (default 50)
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device(focused=True).pinch_out(percent=percent, steps=10)
        
        return {
            "success": True,
            "message": f"Pinch out gesture completed"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def swipe_points(points: List[Tuple[int, int]], duration: float = 0.2, device_id: str = None) -> dict:
    """
    Swipe through multiple points (for pattern unlock).
    
    Args:
        points: List of (x, y) coordinates
        duration: Time between points in seconds
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.swipe_points(points, duration)
        
        return {
            "success": True,
            "message": f"Swiped through {len(points)} points",
            "points_count": len(points)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

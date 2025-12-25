"""
Input Tools - Type Text, Swipe, Scroll
"""
import subprocess
from typing import Optional, Union

from core.device import get_device_connection, DeviceConnectionError
from core.ui_elements import get_ui_elements


def type_text(
    text: str, 
    device_id: Optional[str] = None, 
    clear_first: bool = False
) -> dict:
    """
    Type text into the currently focused input field.
    
    Args:
        text: Text to type
        device_id: Optional device ID
        clear_first: If True, clear existing text before typing
        
    Returns:
        dict with success status and message
    """
    try:
        if not text:
            return {
                "success": False,
                "error": "Text parameter cannot be empty",
                "text": text
            }
        
        device = get_device_connection(device_id)
        
        # Enable fast input IME for reliable text input
        device.set_fastinput_ime(enable=True)
        device.send_keys(text=text, clear=clear_first)
        
        return {
            "success": True,
            "message": "Successfully typed text into input field",
            "text": text,
            "cleared_first": clear_first,
            "action_type": "type_text",
            "device_id": device_id or "default"
        }
        
    except DeviceConnectionError as e:
        return {
            "success": False,
            "error": f"Device connection failed: {e}",
            "text": text
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "text": text
        }


def swipe(
    direction: Optional[str] = None,
    x1: Optional[int] = None,
    y1: Optional[int] = None,
    x2: Optional[int] = None,
    y2: Optional[int] = None,
    device_id: Optional[str] = None,
    distance: Optional[int] = None,
    duration: int = 300
) -> dict:
    """
    Swipe on the Android screen.
    
    Args:
        direction: 'left', 'right', 'up', 'down' for directional swipes
        x1, y1, x2, y2: Exact coordinates for custom swipes
        device_id: Optional device ID
        distance: Distance in pixels (default: 50% of screen)
        duration: Duration in milliseconds (default: 300)
        
    Returns:
        dict with success status and message
    """
    try:
        # Validate input
        if direction and any(c is not None for c in [x1, y1, x2, y2]):
            return {
                "success": False,
                "error": "Provide either direction OR coordinates, not both"
            }
        
        if not direction and not all(c is not None for c in [x1, y1, x2, y2]):
            return {
                "success": False,
                "error": "Provide either direction or exact coordinates (x1, y1, x2, y2)"
            }
        
        if direction:
            # Get screen dimensions for direction-based swipes
            dims = _get_screen_dimensions(device_id)
            if not dims:
                return {
                    "success": False,
                    "error": "Could not determine screen dimensions"
                }
            
            screen_width, screen_height = dims
            
            if distance is None:
                distance = min(screen_width, screen_height) // 2
            
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            direction = direction.lower()
            if direction == 'left':
                x1, y1 = center_x + distance // 2, center_y
                x2, y2 = center_x - distance // 2, center_y
            elif direction == 'right':
                x1, y1 = center_x - distance // 2, center_y
                x2, y2 = center_x + distance // 2, center_y
            elif direction == 'up':
                x1, y1 = center_x, center_y + distance // 2
                x2, y2 = center_x, center_y - distance // 2
            elif direction == 'down':
                x1, y1 = center_x, center_y - distance // 2
                x2, y2 = center_x, center_y + distance // 2
            else:
                return {
                    "success": False,
                    "error": f'Invalid direction: {direction}. Use "left", "right", "up", or "down"'
                }
        
        # Validate coordinates
        if any(c < 0 for c in [x1, y1, x2, y2]):
            return {
                "success": False,
                "error": "All coordinates must be positive"
            }
        
        # Execute swipe
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'input', 'swipe', 
                   str(x1), str(y1), str(x2), str(y2), str(duration)])
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        message = f"Swiped from ({x1}, {y1}) to ({x2}, {y2}) in {duration}ms"
        if direction:
            message = f"Swiped {direction}: " + message
        
        return {
            "success": True,
            "message": message,
            "coordinates": {
                "start": {"x": x1, "y": y1},
                "end": {"x": x2, "y": y2}
            },
            "direction": direction,
            "duration": duration,
            "device_id": device_id or "default"
        }
        
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Failed to execute swipe: {e}"}
    except FileNotFoundError:
        return {"success": False, "error": "ADB not found"}


def scroll_element(
    element: Union[int, str],
    direction: str,
    distance: int = 200,
    duration: int = 300,
    device_id: Optional[str] = None
) -> dict:
    """
    Scroll a specific UI element.
    
    Args:
        element: Element index or name
        direction: 'up', 'down', 'left', 'right'
        distance: Scroll distance in pixels
        duration: Scroll duration in milliseconds
        device_id: Optional device ID
        
    Returns:
        dict with success status and message
    """
    try:
        direction = direction.lower()
        if direction not in ['up', 'down', 'left', 'right']:
            return {
                "success": False,
                "error": f'Invalid direction: {direction}'
            }
        
        if distance <= 0:
            return {
                "success": False,
                "error": "Distance must be positive"
            }
        
        # Get UI elements
        elements = get_ui_elements(device_id)
        if not elements:
            return {
                "success": False,
                "error": "No UI elements found on screen"
            }
        
        # Find target element
        target = None
        if isinstance(element, int):
            if 0 <= element < len(elements):
                target = elements[element]
            else:
                return {
                    "success": False,
                    "error": f"Element index {element} out of range (0-{len(elements)-1})"
                }
        else:
            for elem in elements:
                if elem.name == str(element):
                    target = elem
                    break
            if not target:
                return {
                    "success": False,
                    "error": f"Element '{element}' not found"
                }
        
        # Calculate scroll coordinates within element
        bbox = target.bounding_box
        margin = 20
        center_x = bbox.x1 + bbox.width // 2
        center_y = bbox.y1 + bbox.height // 2
        
        if direction == 'up':
            start_y = min(center_y + distance // 2, bbox.y2 - margin)
            end_y = max(center_y - distance // 2, bbox.y1 + margin)
            start_x = end_x = center_x
        elif direction == 'down':
            start_y = max(center_y - distance // 2, bbox.y1 + margin)
            end_y = min(center_y + distance // 2, bbox.y2 - margin)
            start_x = end_x = center_x
        elif direction == 'left':
            start_x = min(center_x + distance // 2, bbox.x2 - margin)
            end_x = max(center_x - distance // 2, bbox.x1 + margin)
            start_y = end_y = center_y
        else:  # right
            start_x = max(center_x - distance // 2, bbox.x1 + margin)
            end_x = min(center_x + distance // 2, bbox.x2 - margin)
            start_y = end_y = center_y
        
        # Execute scroll
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'input', 'swipe',
                   str(start_x), str(start_y), str(end_x), str(end_y), str(duration)])
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            "success": True,
            "message": f"Scrolled '{target.name}' {direction} for {distance}px",
            "element": target.name,
            "direction": direction,
            "distance": distance,
            "device_id": device_id or "default"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Scroll failed: {e}"}


def _get_screen_dimensions(device_id: Optional[str]) -> Optional[tuple[int, int]]:
    """Helper to get screen dimensions"""
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'wm', 'size'])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        if 'Physical size:' in output:
            size_part = output.split('Physical size:')[1].strip()
            width, height = map(int, size_part.split('x'))
            return width, height
    except Exception:
        pass
    return None

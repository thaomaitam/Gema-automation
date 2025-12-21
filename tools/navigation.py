"""
Navigation Tools - Press, Long Press, Back Button
"""
import subprocess
from typing import Optional

from core.device import get_device_connection, DeviceConnectionError


def press(
    x: int, 
    y: int, 
    device_id: Optional[str] = None, 
    duration: Optional[int] = None
) -> dict:
    """
    Tap on specific coordinates on the Android screen.
    
    Args:
        x: X coordinate to tap
        y: Y coordinate to tap
        device_id: Optional device ID to target
        duration: Duration in milliseconds for long press
        
    Returns:
        dict with success status and message
    """
    try:
        if x < 0 or y < 0:
            return {
                "success": False,
                "error": "Coordinates must be positive integers",
                "x": x, "y": y
            }
        
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        
        if duration and duration > 0:
            # Long press using swipe command
            cmd.extend(['shell', 'input', 'swipe', 
                       str(x), str(y), str(x), str(y), str(duration)])
            action_type = f"long press ({duration}ms)"
        else:
            # Regular tap
            cmd.extend(['shell', 'input', 'tap', str(x), str(y)])
            action_type = "tap"
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            "success": True,
            "message": f"Successfully executed {action_type} at ({x}, {y})",
            "x": x, "y": y,
            "action_type": action_type,
            "device_id": device_id or "default"
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to execute tap: {e}",
            "x": x, "y": y
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "ADB not found. Ensure Android SDK is installed.",
            "x": x, "y": y
        }


def long_press(
    x: int, 
    y: int, 
    device_id: Optional[str] = None
) -> dict:
    """
    Long press on specific coordinates (1.5 seconds).
    
    Args:
        x: X coordinate
        y: Y coordinate
        device_id: Optional device ID
        
    Returns:
        dict with success status and message
    """
    try:
        if x < 0 or y < 0:
            return {
                "success": False,
                "error": "Coordinates must be positive integers",
                "x": x, "y": y
            }
        
        device = get_device_connection(device_id)
        
        # Long press with gesture: stay at position for 1500ms
        device.gesture(
            (x, y, 0),     # touch down immediately
            (x, y, 1500)   # stay for 1.5 seconds
        )
        
        return {
            "success": True,
            "message": f"Successfully executed long press at ({x}, {y}) for 1.5s",
            "x": x, "y": y,
            "duration_ms": 1500,
            "action_type": "long_press",
            "device_id": device_id or "default"
        }
        
    except DeviceConnectionError as e:
        return {
            "success": False,
            "error": f"Device connection failed: {e}",
            "x": x, "y": y
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "x": x, "y": y
        }


def press_back(device_id: Optional[str] = None) -> dict:
    """
    Press the hardware back button.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status and message
    """
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            "success": True,
            "message": "Successfully pressed hardware back button",
            "action_type": "back_press",
            "device_id": device_id or "default"
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to press back button: {e}",
            "action_type": "back_press"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "ADB not found. Ensure Android SDK is installed.",
            "action_type": "back_press"
        }


def open_app(package_name: str, device_id: Optional[str] = None) -> dict:
    """
    Open an Android app by its package name.
    
    Args:
        package_name: Package name of the app (e.g., com.facebook.katana, com.instagram.android)
        device_id: Optional device ID
        
    Returns:
        dict with success status and message
    """
    try:
        if not package_name:
            return {
                "success": False,
                "error": "Package name is required"
            }
        
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        
        # Use monkey to launch the app's main activity
        cmd.extend(['shell', 'monkey', '-p', package_name, 
                   '-c', 'android.intent.category.LAUNCHER', '1'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if 'No activities found' in result.stderr or 'No activities found' in result.stdout:
            return {
                "success": False,
                "error": f"App not found: {package_name}. Make sure the app is installed.",
                "package_name": package_name
            }
        
        return {
            "success": True,
            "message": f"Successfully opened app: {package_name}",
            "package_name": package_name,
            "device_id": device_id or "default"
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to open app: {e}",
            "package_name": package_name
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "ADB not found. Ensure Android SDK is installed.",
            "package_name": package_name
        }


def press_home(device_id: Optional[str] = None) -> dict:
    """
    Press the home button.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            "success": True,
            "message": "Successfully pressed home button",
            "device_id": device_id or "default"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


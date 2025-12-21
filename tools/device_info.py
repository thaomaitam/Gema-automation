"""
Device Info Tools - List Emulators and Dimensions
"""
import subprocess
from typing import Optional

from core.device import get_connected_devices


def list_emulators() -> dict:
    """
    List all available Android emulators and devices.
    
    Returns:
        dict with success status and list of devices
    """
    try:
        devices = get_connected_devices()
        
        return {
            "success": True,
            "devices": devices,
            "count": len(devices)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list devices: {e}",
            "devices": [],
            "count": 0
        }


def get_device_dimensions(device_id: Optional[str] = None) -> dict:
    """
    Get the screen dimensions of the Android device.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status and dimensions
    """
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'wm', 'size'])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        width, height = None, None
        if 'Physical size:' in output:
            size_part = output.split('Physical size:')[1].strip()
            width, height = map(int, size_part.split('x'))
        
        return {
            "success": True,
            "device_id": device_id or "default",
            "width": width,
            "height": height,
            "dimensions": f"{width}x{height}" if width and height else None
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to get dimensions: {e}",
            "device_id": device_id or "default"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "ADB not found. Ensure Android SDK is installed.",
            "device_id": device_id or "default"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "device_id": device_id or "default"
        }

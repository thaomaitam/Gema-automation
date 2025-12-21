"""
App Tools - Application management for Android
"""
import subprocess
from typing import Optional

from core.device import get_device_connection, DeviceConnectionError


def app_start(package_name: str, activity: str = None, stop: bool = False, device_id: str = None) -> dict:
    """
    Start an Android app.
    
    Args:
        package_name: Package name (e.g., com.facebook.katana)
        activity: Optional specific activity to start
        stop: If True, stop the app before starting
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.app_start(package_name, activity=activity, stop=stop)
        
        return {
            "success": True,
            "message": f"Successfully started {package_name}",
            "package_name": package_name
        }
    except Exception as e:
        return {"success": False, "error": str(e), "package_name": package_name}


def app_stop(package_name: str, device_id: str = None) -> dict:
    """
    Stop/force-stop an Android app.
    
    Args:
        package_name: Package name to stop
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.app_stop(package_name)
        
        return {
            "success": True, 
            "message": f"Successfully stopped {package_name}",
            "package_name": package_name
        }
    except Exception as e:
        return {"success": False, "error": str(e), "package_name": package_name}


def app_clear(package_name: str, device_id: str = None) -> dict:
    """
    Clear app data (like uninstall+reinstall).
    
    Args:
        package_name: Package name to clear
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        device.app_clear(package_name)
        
        return {
            "success": True,
            "message": f"Successfully cleared data for {package_name}",
            "package_name": package_name
        }
    except Exception as e:
        return {"success": False, "error": str(e), "package_name": package_name}


def app_current(device_id: str = None) -> dict:
    """
    Get currently running app info (package name and activity).
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with current app info
    """
    try:
        device = get_device_connection(device_id)
        info = device.app_current()
        
        return {
            "success": True,
            "package": info.get("package"),
            "activity": info.get("activity"),
            "message": f"Current app: {info.get('package')}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def app_info(package_name: str, device_id: str = None) -> dict:
    """
    Get app information (version, label, etc.).
    
    Args:
        package_name: Package name
        device_id: Optional device ID
        
    Returns:
        dict with app info
    """
    try:
        device = get_device_connection(device_id)
        info = device.app_info(package_name)
        
        return {
            "success": True,
            "package_name": package_name,
            "label": info.get("label"),
            "version_name": info.get("versionName"),
            "version_code": info.get("versionCode"),
            "main_activity": info.get("mainActivity"),
            "message": f"App: {info.get('label')} v{info.get('versionName')}"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "package_name": package_name}


def app_list(device_id: str = None) -> dict:
    """
    List all installed apps.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with list of package names
    """
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'pm', 'list', 'packages', '-3'])  # -3 for third-party apps
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        packages = [line.replace('package:', '').strip() 
                   for line in result.stdout.strip().split('\n') if line]
        
        return {
            "success": True,
            "packages": packages,
            "count": len(packages),
            "message": f"Found {len(packages)} installed apps"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

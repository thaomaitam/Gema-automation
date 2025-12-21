"""
Android Device Connection Management
Handles uiautomator2 and ADB connections
"""
import subprocess
import uiautomator2 as u2
from typing import Optional


class DeviceConnectionError(Exception):
    """Raised when device connection fails"""
    pass


def validate_adb() -> bool:
    """
    Validate that ADB is installed and accessible.
    
    Returns:
        bool: True if ADB is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['adb', 'version'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_device_connection(device_id: Optional[str] = None) -> u2.Device:
    """
    Establish connection to Android device via uiautomator2.
    
    Args:
        device_id: Optional specific device ID. If None, connects to default device.
        
    Returns:
        u2.Device: Connected device instance
        
    Raises:
        DeviceConnectionError: If connection fails
    """
    try:
        if device_id:
            device = u2.connect(device_id)
        else:
            device = u2.connect()
        
        # Validate connection by accessing device info
        _ = device.info
        return device
        
    except Exception as e:
        raise DeviceConnectionError(
            f"Failed to connect to device '{device_id or 'default'}': {e}"
        )


def get_connected_devices() -> list[dict]:
    """
    List all connected Android devices/emulators.
    
    Returns:
        list[dict]: List of device info dictionaries with:
            - id: Device ID
            - name: Device/AVD name
            - status: Connection status
            - type: 'emulator' or 'device'
            - dimensions: Screen dimensions (if available)
    """
    try:
        result = subprocess.run(
            ['adb', 'devices'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if not line.strip():
                continue
                
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
                
            device_id = parts[0]
            status = parts[1]
            
            device_info = {
                "id": device_id,
                "name": _get_device_name(device_id),
                "status": status,
                "type": "emulator" if device_id.startswith('emulator-') else "device",
                "dimensions": _get_device_dimensions(device_id)
            }
            devices.append(device_info)
            
        return devices
        
    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        return []


def _get_device_name(device_id: str) -> str:
    """Get device/emulator name"""
    try:
        if device_id.startswith('emulator-'):
            # Get AVD name for emulator
            result = subprocess.run(
                ['adb', '-s', device_id, 'emu', 'avd', 'name'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        else:
            # Get model name for physical device
            result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    return "Unknown"


def _get_device_dimensions(device_id: str) -> Optional[str]:
    """Get device screen dimensions"""
    try:
        result = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'wm', 'size'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if 'Physical size:' in output:
                return output.split('Physical size:')[1].strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        pass
    return None

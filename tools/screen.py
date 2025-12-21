"""
Screen Tools - Screenshots and UI Elements
"""
from typing import Optional

from core.screenshot import (
    capture_screenshot, 
    capture_annotated_screenshot,
    save_screenshot
)
from core.ui_elements import get_ui_elements


def take_screenshot(
    device_id: Optional[str] = None,
    name: Optional[str] = None,
    annotate_elements: bool = True
) -> dict:
    """
    Take a screenshot of the device screen.
    
    Args:
        device_id: Optional device ID
        name: Optional filename
        annotate_elements: If True, annotate with UI elements
        
    Returns:
        dict with success status, filepath, and UI elements
    """
    try:
        if annotate_elements:
            # Take annotated screenshot
            image, elements = capture_annotated_screenshot(device_id)
            filepath = save_screenshot(image, name)
            
            elements_info = []
            for i, element in enumerate(elements):
                info = element.to_dict()
                info["index"] = i
                elements_info.append(info)
            
            return {
                "success": True,
                "message": f"Annotated screenshot saved with {len(elements)} UI elements",
                "filepath": filepath,
                "device_id": device_id or "default",
                "ui_elements_count": len(elements),
                "ui_elements": elements_info,
                "annotated": True
            }
        else:
            # Take plain screenshot
            image = capture_screenshot(device_id)
            filepath = save_screenshot(image, name)
            
            return {
                "success": True,
                "message": "Screenshot saved successfully",
                "filepath": filepath,
                "device_id": device_id or "default",
                "annotated": False
            }
            
    except RuntimeError as e:
        return {
            "success": False,
            "error": str(e),
            "filepath": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "filepath": None
        }


def get_ui_elements_info(device_id: Optional[str] = None) -> dict:
    """
    Get information about all interactive UI elements on screen.
    
    Args:
        device_id: Optional device ID
        
    Returns:
        dict with success status and list of UI elements
    """
    try:
        elements = get_ui_elements(device_id)
        
        elements_info = []
        for i, element in enumerate(elements):
            info = element.to_dict()
            info["index"] = i
            elements_info.append(info)
        
        return {
            "success": True,
            "message": f"Found {len(elements)} interactive UI elements",
            "device_id": device_id or "default",
            "elements": elements_info,
            "count": len(elements)
        }
        
    except RuntimeError as e:
        return {
            "success": False,
            "error": str(e),
            "elements": [],
            "count": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "elements": [],
            "count": 0
        }

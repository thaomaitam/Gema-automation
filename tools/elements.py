"""
Element Tools - UI element interactions using selectors
"""
from typing import Optional, Dict, Any

from core.device import get_device_connection, DeviceConnectionError


def click_element(text: str = None, resource_id: str = None, class_name: str = None,
                  description: str = None, timeout: float = 10, device_id: str = None) -> dict:
    """
    Click a UI element by selector (text, resource-id, class, or description).
    
    Args:
        text: Element text to find
        resource_id: Resource ID (e.g., com.app:id/button)
        class_name: Class name (e.g., android.widget.Button)
        description: Content description
        timeout: Wait timeout in seconds
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        selector = {}
        if text:
            selector['text'] = text
        if resource_id:
            selector['resourceId'] = resource_id
        if class_name:
            selector['className'] = class_name
        if description:
            selector['description'] = description
        
        if not selector:
            return {"success": False, "error": "At least one selector required"}
        
        element = device(**selector)
        if element.exists(timeout=timeout):
            element.click()
            return {
                "success": True,
                "message": f"Clicked element with {list(selector.keys())[0]}={list(selector.values())[0]}",
                "selector": selector
            }
        else:
            return {"success": False, "error": "Element not found", "selector": selector}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def long_click_element(text: str = None, resource_id: str = None, 
                       duration: float = 0.5, device_id: str = None) -> dict:
    """
    Long click a UI element.
    
    Args:
        text: Element text to find
        resource_id: Resource ID
        duration: Long click duration in seconds
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        if text:
            element = device(text=text)
        elif resource_id:
            element = device(resourceId=resource_id)
        else:
            return {"success": False, "error": "text or resource_id required"}
        
        if element.exists:
            element.long_click(duration=duration)
            return {"success": True, "message": f"Long clicked element"}
        else:
            return {"success": False, "error": "Element not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_element_info(text: str = None, resource_id: str = None, device_id: str = None) -> dict:
    """
    Get detailed info about a specific UI element.
    
    Args:
        text: Element text to find
        resource_id: Resource ID
        device_id: Optional device ID
        
    Returns:
        dict with element info (bounds, text, class, etc.)
    """
    try:
        device = get_device_connection(device_id)
        
        if text:
            element = device(text=text)
        elif resource_id:
            element = device(resourceId=resource_id)
        else:
            return {"success": False, "error": "text or resource_id required"}
        
        if element.exists:
            info = element.info
            return {
                "success": True,
                "text": info.get("text"),
                "className": info.get("className"),
                "bounds": info.get("bounds"),
                "clickable": info.get("clickable"),
                "enabled": info.get("enabled"),
                "selected": info.get("selected"),
                "message": f"Found element: {info.get('text', info.get('className'))}"
            }
        else:
            return {"success": False, "error": "Element not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def wait_element(text: str = None, resource_id: str = None, 
                timeout: float = 10, device_id: str = None) -> dict:
    """
    Wait for a UI element to appear.
    
    Args:
        text: Element text to wait for
        resource_id: Resource ID to wait for
        timeout: Wait timeout in seconds
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        if text:
            element = device(text=text)
        elif resource_id:
            element = device(resourceId=resource_id)
        else:
            return {"success": False, "error": "text or resource_id required"}
        
        appeared = element.wait(timeout=timeout)
        
        if appeared:
            return {"success": True, "message": f"Element appeared within {timeout}s"}
        else:
            return {"success": False, "error": f"Element did not appear within {timeout}s"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def wait_element_gone(text: str = None, resource_id: str = None,
                      timeout: float = 10, device_id: str = None) -> dict:
    """
    Wait for a UI element to disappear.
    
    Args:
        text: Element text
        resource_id: Resource ID
        timeout: Wait timeout in seconds
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        if text:
            element = device(text=text)
        elif resource_id:
            element = device(resourceId=resource_id)
        else:
            return {"success": False, "error": "text or resource_id required"}
        
        gone = element.wait_gone(timeout=timeout)
        
        if gone:
            return {"success": True, "message": f"Element disappeared within {timeout}s"}
        else:
            return {"success": False, "error": f"Element still present after {timeout}s"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_element_text(text: str, input_text: str = None, resource_id: str = None, 
                     device_id: str = None) -> dict:
    """
    Set text in an input field element.
    
    Args:
        text: Element text to find (the input field)
        input_text: Text to input
        resource_id: Resource ID of input field
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        if resource_id:
            element = device(resourceId=resource_id)
        elif text:
            element = device(text=text)
        else:
            return {"success": False, "error": "text or resource_id required"}
        
        if element.exists:
            element.set_text(input_text or "")
            return {"success": True, "message": f"Set text: {input_text}"}
        else:
            return {"success": False, "error": "Element not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def scroll_to_element(text: str, device_id: str = None) -> dict:
    """
    Scroll to find an element.
    
    Args:
        text: Element text to scroll to
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        scrollable = device(scrollable=True)
        if scrollable.exists:
            scrollable.scroll.to(text=text)
            return {"success": True, "message": f"Scrolled to element: {text}"}
        else:
            return {"success": False, "error": "No scrollable element found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def xpath_click(xpath: str, timeout: float = 10, device_id: str = None) -> dict:
    """
    Click element using XPath selector.
    
    Args:
        xpath: XPath expression (e.g., '//*[@text="Settings"]', '@com.app:id/button')
        timeout: Wait timeout
        device_id: Optional device ID
        
    Returns:
        dict with success status
    """
    try:
        device = get_device_connection(device_id)
        
        element = device.xpath(xpath)
        if element.wait(timeout=timeout):
            element.click()
            return {"success": True, "message": f"Clicked XPath: {xpath}"}
        else:
            return {"success": False, "error": f"XPath element not found: {xpath}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def xpath_get_text(xpath: str, device_id: str = None) -> dict:
    """
    Get text from element using XPath.
    
    Args:
        xpath: XPath expression
        device_id: Optional device ID
        
    Returns:
        dict with element text
    """
    try:
        device = get_device_connection(device_id)
        
        text = device.xpath(xpath).get_text()
        return {"success": True, "text": text, "message": f"Text: {text}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

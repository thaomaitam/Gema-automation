"""
UI Element Detection and Parsing
Extracts interactive elements from Android UI hierarchy
"""
import re
from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree

from .device import get_device_connection

# Interactive element classes (common Android UI elements)
INTERACTIVE_CLASSES = [
    "android.widget.Button",
    "android.widget.ImageButton",
    "android.widget.EditText",
    "android.widget.CheckBox",
    "android.widget.RadioButton",
    "android.widget.Switch",
    "android.widget.ToggleButton",
    "android.widget.Spinner",
    "android.widget.SeekBar",
    "android.widget.RatingBar",
    "android.widget.TabHost",
    "android.widget.NumberPicker",
    "android.support.v7.widget.RecyclerView",
    "androidx.recyclerview.widget.RecyclerView",
    "android.widget.ListView",
    "android.widget.GridView",
    "android.widget.ScrollView",
    "android.widget.HorizontalScrollView",
    "androidx.viewpager.widget.ViewPager",
    "androidx.viewpager2.widget.ViewPager2"
]


@dataclass
class BoundingBox:
    """Represents element bounding box coordinates"""
    x1: int
    y1: int
    x2: int
    y2: int

    def to_string(self) -> str:
        return f'[{self.x1},{self.y1}][{self.x2},{self.y2}]'
    
    @property
    def width(self) -> int:
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        return self.y2 - self.y1


@dataclass
class CenterCord:
    """Represents center coordinates of an element"""
    x: int
    y: int

    def to_string(self) -> str:
        return f'({self.x},{self.y})'


@dataclass
class ElementNode:
    """Represents a UI element with all its properties"""
    name: str
    coordinates: CenterCord
    bounding_box: BoundingBox
    class_name: str = ""
    clickable: bool = False
    focusable: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "center_coordinates": {
                "x": self.coordinates.x,
                "y": self.coordinates.y
            },
            "bounding_box": {
                "x1": self.bounding_box.x1,
                "y1": self.bounding_box.y1,
                "x2": self.bounding_box.x2,
                "y2": self.bounding_box.y2
            },
            "class_name": self.class_name,
            "clickable": self.clickable,
            "focusable": self.focusable
        }


def extract_coordinates(node) -> Optional[tuple[int, int, int, int]]:
    """
    Extract coordinates from Android UI hierarchy node bounds attribute.
    
    Args:
        node: XML element node with 'bounds' attribute
        
    Returns:
        Tuple of (x1, y1, x2, y2) or None if parsing fails
    """
    bounds = node.attrib.get('bounds')
    if not bounds:
        return None
        
    match = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    if match:
        return tuple(map(int, match.groups()))
    return None


def get_center_coordinates(coords: tuple[int, int, int, int]) -> tuple[int, int]:
    """
    Calculate center coordinates from bounding box.
    
    Args:
        coords: Tuple of (x1, y1, x2, y2)
        
    Returns:
        Tuple of (center_x, center_y)
    """
    x1, y1, x2, y2 = coords
    return (x1 + x2) // 2, (y1 + y2) // 2


def get_element_name(node) -> str:
    """
    Get a human-readable name for the UI element.
    
    Priority: text content > content-desc > class name
    """
    # Try to get text from child TextView elements
    text_parts = []
    for child in node:
        if child.get('class') == 'android.widget.TextView':
            text = child.get('text') or child.get('content-desc')
            if text:
                text_parts.append(text)
    
    if text_parts:
        return " ".join(text_parts)
    
    # Try content-desc or text on the node itself
    name = node.get('content-desc') or node.get('text')
    if name:
        return name
    
    # Fallback to class name
    class_name = node.get('class', 'Unknown')
    return class_name.split('.')[-1]


def is_interactive(node) -> bool:
    """
    Check if a UI element is interactive.
    
    An element is considered interactive if:
    - It's focusable OR
    - It's clickable OR
    - Its class is in the list of interactive classes
    """
    attribs = node.attrib
    return (
        attribs.get('focusable') == "true" or
        attribs.get('clickable') == "true" or
        attribs.get('class') in INTERACTIVE_CLASSES
    )


def get_ui_elements(device_id: Optional[str] = None) -> list[ElementNode]:
    """
    Get all interactive UI elements from the device screen.
    
    Args:
        device_id: Optional device ID to target
        
    Returns:
        List of ElementNode objects representing interactive elements
        
    Raises:
        RuntimeError: If UI hierarchy cannot be retrieved
    """
    try:
        device = get_device_connection(device_id)
        
        # Get UI hierarchy XML
        tree_string = device.dump_hierarchy()
        element_tree = ElementTree.fromstring(tree_string)
        
        elements = []
        # Find all visible and enabled nodes
        nodes = element_tree.findall('.//*[@visible-to-user="true"][@enabled="true"]')
        
        for node in nodes:
            if not is_interactive(node):
                continue
                
            coords = extract_coordinates(node)
            if not coords:
                continue
                
            name = get_element_name(node)
            if not name:
                continue
                
            x1, y1, x2, y2 = coords
            center_x, center_y = get_center_coordinates(coords)
            
            element = ElementNode(
                name=name,
                coordinates=CenterCord(x=center_x, y=center_y),
                bounding_box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                class_name=node.get('class', ''),
                clickable=node.get('clickable') == 'true',
                focusable=node.get('focusable') == 'true'
            )
            elements.append(element)
            
        return elements
        
    except Exception as e:
        raise RuntimeError(f"Failed to get UI elements: {e}")

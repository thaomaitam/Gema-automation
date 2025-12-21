"""
Screenshot Capture and Annotation
Handles screenshot capture and UI element visualization
"""
import subprocess
import io
import random
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

from .ui_elements import ElementNode, get_ui_elements
import config


def capture_screenshot(device_id: Optional[str] = None) -> Image.Image:
    """
    Capture a raw screenshot from the device.
    
    Args:
        device_id: Optional device ID to target
        
    Returns:
        PIL Image object
        
    Raises:
        RuntimeError: If screenshot capture fails
    """
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['exec-out', 'screencap', '-p'])
        
        result = subprocess.run(cmd, capture_output=True, check=True)
        return Image.open(io.BytesIO(result.stdout))
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to capture screenshot: {e}")
    except FileNotFoundError:
        raise RuntimeError("ADB not found. Ensure Android SDK is installed.")


def annotate_screenshot(
    screenshot: Image.Image, 
    elements: list[ElementNode]
) -> Image.Image:
    """
    Annotate screenshot with UI element bounding boxes and labels.
    
    Args:
        screenshot: PIL Image to annotate
        elements: List of ElementNode objects to draw
        
    Returns:
        Annotated PIL Image
    """
    # Create a copy to avoid modifying original
    annotated = screenshot.copy()
    draw = ImageDraw.Draw(annotated)
    
    # Try to load a font
    font = _get_font(12)
    
    for idx, element in enumerate(elements):
        color = _get_random_color()
        _draw_element_annotation(draw, idx, element, color, font, annotated.width)
    
    return annotated


def capture_annotated_screenshot(
    device_id: Optional[str] = None
) -> tuple[Image.Image, list[ElementNode]]:
    """
    Capture screenshot and annotate with UI elements.
    
    Args:
        device_id: Optional device ID to target
        
    Returns:
        Tuple of (annotated_image, list_of_elements)
    """
    screenshot = capture_screenshot(device_id)
    elements = get_ui_elements(device_id)
    annotated = annotate_screenshot(screenshot, elements)
    return annotated, elements


def save_screenshot(
    image: Image.Image, 
    name: Optional[str] = None
) -> str:
    """
    Save screenshot to the screenshots directory.
    
    Args:
        image: PIL Image to save
        name: Optional filename (without extension)
        
    Returns:
        Full path to saved file
    """
    import os
    
    if name:
        filename = f"{name}.png" if not name.endswith('.png') else name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    filepath = os.path.join(config.SCREENSHOTS_DIR, filename)
    image.save(filepath, 'PNG')
    return filepath


# ============================================================
# Private Helper Functions
# ============================================================

def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Try to load a font, fallback to default if unavailable"""
    font_paths = [
        'arial.ttf',
        '/System/Library/Fonts/Arial.ttf',
        'C:\\Windows\\Fonts\\arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    
    return ImageFont.load_default()


def _get_random_color() -> str:
    """Generate a random hex color"""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def _draw_element_annotation(
    draw: ImageDraw.Draw,
    index: int,
    element: ElementNode,
    color: str,
    font: ImageFont.FreeTypeFont,
    image_width: int
) -> None:
    """Draw bounding box and label for a single element"""
    bbox = element.bounding_box
    
    # Draw bounding box
    draw.rectangle(
        [(bbox.x1, bbox.y1), (bbox.x2, bbox.y2)],
        outline=color,
        width=2
    )
    
    # Prepare label
    label_text = f"{index}: {element.name}"
    text_bbox = draw.textbbox((0, 0), label_text, font=font)
    label_width = text_bbox[2] - text_bbox[0]
    label_height = text_bbox[3] - text_bbox[1]
    
    # Position label above bounding box
    label_x1 = max(bbox.x1, 0)
    label_y1 = max(bbox.y1 - label_height - 4, 0)
    label_x2 = min(label_x1 + label_width + 4, image_width - 1)
    label_y2 = label_y1 + label_height + 4
    
    # Draw label background and text
    draw.rectangle([(label_x1, label_y1), (label_x2, label_y2)], fill=color)
    draw.text((label_x1 + 2, label_y1 + 2), label_text, fill=(255, 255, 255), font=font)

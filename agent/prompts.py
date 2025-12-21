"""
System Prompts and Tool Schemas for Ollama
Defines the agent's behavior and available tools
"""

SYSTEM_PROMPT = """You are an intelligent Android automation agent. Your purpose is to help users automate tasks on their Android devices by using the available tools.

## Your Capabilities
You can interact with Android devices through:
- **Screen Observation**: Take screenshots to understand the current state
- **Navigation**: Tap on elements, press back, swipe in directions
- **Input**: Type text into fields
- **Information**: Get UI elements, device dimensions, list devices
- **Recording**: Start/stop video recordings

## Workflow Guidelines
1. **Always start by observing**: Use `take_screenshot` to understand the current screen state
2. **Analyze UI elements**: The screenshot tool returns annotated elements with indexes and coordinates
3. **Plan your actions**: Think step-by-step about how to accomplish the task
4. **Execute carefully**: Perform one action at a time and verify results
5. **Report completion**: Clearly communicate when the task is done

## Important Notes
- Use element coordinates from the UI elements info to tap on specific items
- Wait briefly after each action for the UI to update
- If something doesn't work, try an alternative approach
- Ask for clarification if the task is ambiguous

You have access to the following tools to accomplish tasks on Android devices."""


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the device screen. Returns annotated image with UI elements indexed and their coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID. If not provided, uses default device."
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional filename for the screenshot"
                    },
                    "annotate_elements": {
                        "type": "boolean",
                        "description": "If true, annotate screenshot with UI element bounding boxes and indexes. Default: true"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ui_elements_info",
            "description": "Get detailed information about all interactive UI elements on the current screen, including their names, coordinates, and properties.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press",
            "description": "Tap on specific screen coordinates. Use coordinates from UI elements to tap on specific items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate to tap"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate to tap"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Duration in milliseconds for long press"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "long_press",
            "description": "Long press on specific coordinates for 1.5 seconds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_back",
            "description": "Press the hardware back button on the Android device.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text into the currently focused input field.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    },
                    "clear_first": {
                        "type": "boolean",
                        "description": "If true, clear existing text before typing"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "swipe",
            "description": "Swipe on the screen. Use direction for simple swipes, or specify exact coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["left", "right", "up", "down"],
                        "description": "Swipe direction"
                    },
                    "x1": {"type": "integer", "description": "Start X coordinate"},
                    "y1": {"type": "integer", "description": "Start Y coordinate"},
                    "x2": {"type": "integer", "description": "End X coordinate"},
                    "y2": {"type": "integer", "description": "End Y coordinate"},
                    "device_id": {"type": "string", "description": "Optional device ID"},
                    "distance": {"type": "integer", "description": "Swipe distance in pixels"},
                    "duration": {"type": "integer", "description": "Duration in milliseconds"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll_element",
            "description": "Scroll within a specific UI element.",
            "parameters": {
                "type": "object",
                "properties": {
                    "element": {
                        "type": ["integer", "string"],
                        "description": "Element index (from UI elements) or element name"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "Scroll direction"
                    },
                    "distance": {
                        "type": "integer",
                        "description": "Scroll distance in pixels (default: 200)"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Duration in milliseconds (default: 300)"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    }
                },
                "required": ["element", "direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_emulators",
            "description": "List all available Android emulators and connected devices.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_dimensions",
            "description": "Get the screen dimensions (width x height) of the Android device.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_video",
            "description": "Start recording a video of the device screen using scrcpy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Optional device ID"},
                    "filename": {"type": "string", "description": "Optional filename"},
                    "resolution": {"type": "string", "description": "Optional max resolution"},
                    "bitrate": {"type": "string", "description": "Video bitrate (default: 8M)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_video",
            "description": "Stop the active video recording.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Optional device ID"
                    }
                },
                "required": []
            }
        }
    }
]

"""
Gemma Agent - Ollama with Tool Calling
Supports both native tool calling and prompt-based fallback
Full uiautomator2 capabilities
"""
import json
import re
from typing import Optional

import ollama
from ollama import ChatResponse

from tools import TOOL_REGISTRY
import config


# Tool wrapper functions with docstrings for native tool calling
def take_screenshot(device_id: str = None, annotate_elements: bool = True) -> dict:
    """Take a screenshot of the Android device screen with UI annotations."""
    return TOOL_REGISTRY["take_screenshot"](device_id=device_id, annotate_elements=annotate_elements)

def get_ui_elements_info(device_id: str = None) -> dict:
    """Get info about all interactive UI elements on screen."""
    return TOOL_REGISTRY["get_ui_elements_info"](device_id=device_id)

def press(x: int, y: int, device_id: str = None) -> dict:
    """Tap on coordinates (x, y) on the Android screen."""
    return TOOL_REGISTRY["press"](x=int(x), y=int(y), device_id=device_id)

def press_back(device_id: str = None) -> dict:
    """Press the hardware back button."""
    return TOOL_REGISTRY["press_back"](device_id=device_id)

def press_home(device_id: str = None) -> dict:
    """Press the home button."""
    return TOOL_REGISTRY["press_home"](device_id=device_id)

def type_text(text: str, clear_first: bool = False, device_id: str = None) -> dict:
    """Type text into the focused input field."""
    return TOOL_REGISTRY["type_text"](text=text, device_id=device_id, clear_first=clear_first)

def swipe(direction: str, device_id: str = None) -> dict:
    """Swipe on screen. Direction: 'up', 'down', 'left', 'right'."""
    return TOOL_REGISTRY["swipe"](direction=direction, device_id=device_id)

def list_emulators() -> dict:
    """List all connected Android devices."""
    return TOOL_REGISTRY["list_emulators"]()

def get_device_dimensions(device_id: str = None) -> dict:
    """Get the screen dimensions of the device."""
    return TOOL_REGISTRY["get_device_dimensions"](device_id=device_id)

def app_start(package_name: str, stop: bool = False, device_id: str = None) -> dict:
    """Start an Android app by package name. Example: com.facebook.katana for Facebook."""
    result = TOOL_REGISTRY["app_start"](package_name=package_name, stop=stop, device_id=device_id)
    # Auto-wait 2 seconds for app to start loading
    import time
    time.sleep(2)
    result["message"] = result.get("message", "") + " (đã đợi 2 giây để app load)"
    return result

def app_stop(package_name: str, device_id: str = None) -> dict:
    """Force stop an Android app."""
    return TOOL_REGISTRY["app_stop"](package_name=package_name, device_id=device_id)

def app_current(device_id: str = None) -> dict:
    """Get currently running app info."""
    return TOOL_REGISTRY["app_current"](device_id=device_id)

def double_click(x: int, y: int, device_id: str = None) -> dict:
    """Double click at coordinates."""
    return TOOL_REGISTRY["double_click"](x=int(x), y=int(y), device_id=device_id)

def drag(sx: int, sy: int, ex: int, ey: int, device_id: str = None) -> dict:
    """Drag from (sx,sy) to (ex,ey)."""
    return TOOL_REGISTRY["drag"](sx=int(sx), sy=int(sy), ex=int(ex), ey=int(ey), device_id=device_id)

def screen_on(device_id: str = None) -> dict:
    """Turn on the screen."""
    return TOOL_REGISTRY["screen_on"](device_id=device_id)

def screen_off(device_id: str = None) -> dict:
    """Turn off the screen."""
    return TOOL_REGISTRY["screen_off"](device_id=device_id)

def unlock(device_id: str = None) -> dict:
    """Unlock the device screen."""
    return TOOL_REGISTRY["unlock"](device_id=device_id)

def send_keys(text: str, clear: bool = False, device_id: str = None) -> dict:
    """Send text using input method."""
    return TOOL_REGISTRY["send_keys"](text=text, clear=clear, device_id=device_id)

def clear_text(device_id: str = None) -> dict:
    """Clear text in focused input field."""
    return TOOL_REGISTRY["clear_text"](device_id=device_id)

def hide_keyboard(device_id: str = None) -> dict:
    """Hide the soft keyboard."""
    return TOOL_REGISTRY["hide_keyboard"](device_id=device_id)

def open_notification(device_id: str = None) -> dict:
    """Open notification panel."""
    return TOOL_REGISTRY["open_notification"](device_id=device_id)

def open_quick_settings(device_id: str = None) -> dict:
    """Open quick settings panel."""
    return TOOL_REGISTRY["open_quick_settings"](device_id=device_id)

def shell(command: str, device_id: str = None) -> dict:
    """Execute a shell command on the device."""
    return TOOL_REGISTRY["shell"](command=command, device_id=device_id)

def click_element(text: str = None, resource_id: str = None, timeout: float = 10, device_id: str = None) -> dict:
    """Click UI element by text or resource_id."""
    return TOOL_REGISTRY["click_element"](text=text, resource_id=resource_id, timeout=timeout, device_id=device_id)

def wait_element(text: str = None, resource_id: str = None, timeout: float = 10, device_id: str = None) -> dict:
    """Wait for UI element to appear."""
    return TOOL_REGISTRY["wait_element"](text=text, resource_id=resource_id, timeout=timeout, device_id=device_id)

def xpath_click(xpath: str, timeout: float = 10, device_id: str = None) -> dict:
    """Click element using XPath (e.g., '//*[@text=\"Settings\"]')."""
    return TOOL_REGISTRY["xpath_click"](xpath=xpath, timeout=timeout, device_id=device_id)

def scroll_to_element(text: str, device_id: str = None) -> dict:
    """Scroll to find an element by text."""
    return TOOL_REGISTRY["scroll_to_element"](text=text, device_id=device_id)


# All tools available for native tool calling
AVAILABLE_TOOLS = [
    take_screenshot, get_ui_elements_info, press, press_back, press_home, 
    type_text, swipe, list_emulators, get_device_dimensions,
    app_start, app_stop, app_current,
    double_click, drag,
    screen_on, screen_off, unlock,
    send_keys, clear_text, hide_keyboard,
    open_notification, open_quick_settings, shell,
    click_element, wait_element, xpath_click, scroll_to_element
]

TOOL_FUNCTIONS = {func.__name__: func for func in AVAILABLE_TOOLS}

# Enhanced prompt with agentic workflow
FALLBACK_PROMPT = """# 🤖 ANDROID AUTOMATION AGENT

Bạn là agent thông minh điều khiển điện thoại Android THẬT. Bạn làm việc theo quy trình chuyên nghiệp.

## 🔄 QUY TRÌNH LÀM VIỆC

### 1️⃣ PLAN (Phân tích & Lên kế hoạch)
Khi nhận yêu cầu, BẮT ĐẦU bằng việc phân tích:
```
📋 PHÂN TÍCH:
- Yêu cầu: [mô tả ngắn gọn yêu cầu user]
- Mục tiêu: [kết quả mong muốn]
- Các bước cần làm:
  1. [bước 1]
  2. [bước 2]
  ...
```

### 2️⃣ EXECUTE (Thực hiện)
Sau đó gọi tool:
```json
{"tool": "tool_name", "args": {"param": "value"}}
```

### 3️⃣ VERIFY (Kiểm tra)
Sau mỗi tool, đánh giá kết quả:
- ✅ Thành công → Tiếp tục bước tiếp theo
- ❌ Thất bại → Phân tích lý do, thử cách khác

### 4️⃣ REPORT (Báo cáo)
Khi hoàn thành, báo cáo:
```
📊 KẾT QUẢ:
- Đã thực hiện: [liệt kê các bước đã làm]
- Trạng thái: [thành công/thất bại]
- Ghi chú: [thông tin thêm nếu có]
```

## 🛠️ TOOLS CÓ SẴN

### App Management
- `app_start`: Mở app. Args: package_name
- `app_stop`: Tắt app. Args: package_name
- `app_current`: Xem app đang chạy

### Touch/Input
- `press`: Tap tọa độ x, y
- `click_element`: Click element theo text
- `type_text`: Gõ chữ. Args: text
- `swipe`: Vuốt. Args: direction (up/down/left/right)
- `press_back`: Nút Back
- `press_home`: Nút Home

### Screen/UI
- `take_screenshot`: Chụp màn hình + phân tích UI
- `get_ui_elements_info`: Lấy danh sách UI elements
- `wait_element`: Đợi element xuất hiện
- `scroll_to_element`: Cuộn tìm element

### System
- `shell`: Chạy lệnh ADB

## 📱 PACKAGES PHỔ BIẾN
- Facebook: com.facebook.katana
- Messenger: com.facebook.orca
- Instagram: com.instagram.android
- YouTube: com.google.android.youtube
- Chrome: com.android.chrome
- Zalo: com.zing.zalo

## 💡 VÍ DỤ HOÀN CHỈNH

User: "Mở Facebook và tìm nhóm OpenWRT Việt Nam"

```
📋 PHÂN TÍCH:
- Yêu cầu: Truy cập nhóm OpenWRT Việt Nam trên Facebook
- Mục tiêu: Vào được trang nhóm
- Các bước cần làm:
  1. Mở app Facebook
  2. Chờ app load
  3. Chụp màn hình xem giao diện
  4. Tìm ô tìm kiếm và click
  5. Gõ "OpenWRT Việt Nam"
  6. Click vào kết quả nhóm
```

Bắt đầu thực hiện bước 1:
```json
{"tool": "app_start", "args": {"package_name": "com.facebook.katana"}}
```

[Sau khi tool chạy xong]

✅ Bước 1 OK. Tiếp tục bước 2-3:
```json
{"tool": "take_screenshot", "args": {}}
```

[Tiếp tục...]

## ⚠️ LƯU Ý QUAN TRỌNG
1. LUÔN bắt đầu bằng PHÂN TÍCH
2. SAU mỗi tool, đánh giá kết quả trước khi tiếp tục
3. NẾU lỗi, thử cách khác (ví dụ: thay click_element bằng press + tọa độ)
4. CUỐI CÙNG báo cáo kết quả cho user

Trả lời bằng tiếng Việt. Giao tiếp thân thiện và chuyên nghiệp."""


NATIVE_PROMPT = """🤖 Android Automation Agent

Bạn là agent thông minh điều khiển điện thoại Android. Làm việc theo quy trình:

1. 📋 PHÂN TÍCH yêu cầu và lên kế hoạch
2. ⚡ THỰC HIỆN từng bước bằng tools
3. ✅ KIỂM TRA kết quả sau mỗi bước
4. 💬 BÁO CÁO kết quả cuối cùng

Package: Facebook=com.facebook.katana, Instagram=com.instagram.android

Trả lời bằng tiếng Việt. Giao tiếp thân thiện!"""


# Ollama options for better performance
OLLAMA_OPTIONS = {
    "num_ctx": 16384,  # Context length 16k
    "temperature": 0.7,
}


class GemmaAgent:
    """Agent with fallback for non-tool-calling models"""
    
    def __init__(self, model: str = None):
        self.model = model or config.DEFAULT_MODEL
        self.messages: list[dict] = []
        self.use_native_tools = True  # Try native first
        self.max_iterations = 10  # Max tool calls per request
        self._init_conversation()
    
    def _init_conversation(self) -> None:
        prompt = NATIVE_PROMPT if self.use_native_tools else FALLBACK_PROMPT
        self.messages = [{"role": "system", "content": prompt}]
    
    def reset(self) -> None:
        self._init_conversation()
    
    def chat(self, user_input: str, verbose: bool = True) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        if self.use_native_tools:
            try:
                return self._chat_native(verbose)
            except Exception as e:
                if "does not support tools" in str(e):
                    self.use_native_tools = False
                    self.messages = [{"role": "system", "content": FALLBACK_PROMPT}]
                    self.messages.append({"role": "user", "content": user_input})
                    return self._chat_fallback(verbose)
                raise
        else:
            return self._chat_fallback(verbose)
    
    def _chat_native(self, verbose: bool) -> str:
        response: ChatResponse = ollama.chat(
            model=self.model,
            messages=self.messages,
            tools=AVAILABLE_TOOLS,
            options=OLLAMA_OPTIONS
        )
        
        iterations = 0
        while response.message.tool_calls and iterations < self.max_iterations:
            iterations += 1
            self.messages.append(response.message)
            
            for tool in response.message.tool_calls:
                result = self._execute_tool(tool.function.name, tool.function.arguments or {}, verbose)
                self.messages.append({"role": "tool", "content": result, "tool_name": tool.function.name})
            
            response = ollama.chat(
                model=self.model, 
                messages=self.messages, 
                tools=AVAILABLE_TOOLS,
                options=OLLAMA_OPTIONS
            )
        
        self.messages.append(response.message)
        return response.message.content or ""
    
    def _chat_fallback(self, verbose: bool) -> str:
        """Fallback with improved multi-action handling"""
        response = ollama.chat(
            model=self.model, 
            messages=self.messages,
            options=OLLAMA_OPTIONS
        )
        content = response.message.content or ""
        self.messages.append({"role": "assistant", "content": content})
        
        # Parse and execute tools in a loop
        iterations = 0
        while iterations < self.max_iterations:
            iterations += 1
            
            tool_call = self._parse_tool_json(content)
            
            if not tool_call:
                break
                
            tool_name, tool_args = tool_call
            result = self._execute_tool(tool_name, tool_args, verbose)
            
            # Ask model to continue with remaining tasks
            self.messages.append({
                "role": "user", 
                "content": f"Tool `{tool_name}` thành công:\n```json\n{result}\n```\n\nCòn hành động nào cần thực hiện không? Nếu có, gọi tool tiếp theo. Nếu hoàn thành rồi, tóm tắt kết quả."
            })
            
            follow_up = ollama.chat(
                model=self.model, 
                messages=self.messages,
                options=OLLAMA_OPTIONS
            )
            content = follow_up.message.content or ""
            self.messages.append({"role": "assistant", "content": content})
        
        return content
    
    def _execute_tool(self, name: str, args: dict, verbose: bool) -> str:
        if verbose:
            print(f"\n🔧 Calling: {name}")
            if args:
                print(f"   Args: {args}")
        
        func = TOOL_FUNCTIONS.get(name)
        if not func:
            result = {"success": False, "error": f"Tool {name} not found"}
        else:
            try:
                result = func(**args)
            except Exception as e:
                result = {"success": False, "error": str(e)}
        
        if verbose:
            icon = "✅" if result.get("success") else "❌"
            msg = result.get("message", result.get("error", ""))
            print(f"   {icon} {msg}")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def _parse_tool_json(self, text: str) -> Optional[tuple[str, dict]]:
        patterns = [
            r'```(?:json)?\s*(\{[^`]+\})\s*```',
            r'(\{"tool":\s*"[^"]+"\s*(?:,\s*"args"\s*:\s*\{[^}]*\})?\s*\})',
        ]
        
        for pattern in patterns:
            for match in re.findall(pattern, text, re.DOTALL):
                try:
                    data = json.loads(match)
                    if data.get("tool") in TOOL_FUNCTIONS:
                        return (data["tool"], data.get("args", {}))
                except:
                    continue
        return None


def list_available_models() -> list[str]:
    try:
        models = ollama.list()
        return [m.model if hasattr(m, 'model') else str(m) for m in models.get("models", [])]
    except:
        return []


def check_model_available(model: str) -> bool:
    return any(model in m for m in list_available_models())

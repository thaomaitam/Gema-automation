"""
Planner Brain - Generates execution plan before navigation.

Part of the Planner-Navigator architecture:
- Planner (this): Generates high-level JSON plan with reasoning
- Navigator: Executes each step using tools

Uses a high-capability model (gemini-2.5-pro) for strategic planning.
"""
import os
import json
import requests
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
import base64

from agent.brain import Brain, ThinkResult


PLANNER_SYSTEM_PROMPT = """Bạn là Android Automation Planner. Nhiệm vụ của bạn là TẠO KẾ HOẠCH, KHÔNG THỰC THI.

## VAI TRÒ
- Bạn là CHIẾN LƯỢC GIA (Planner), không phải người thực thi (Navigator)
- Bạn phân tích yêu cầu của User và tạo ra danh sách các BƯỚC LỚN (High-level Goals)
- Mỗi bước phải RÕ RÀNG, CÓ THỂ THỰC HIỆN ĐƯỢC bởi Navigator

## TOOLS CÓ SẴN (với tham số chính xác)

### App Management
- `app_start(package_name)` - Mở ứng dụng
- `app_stop(package_name)` - Đóng ứng dụng  
- `app_current()` - Lấy package đang chạy

### Element Interaction (Quan trọng!)
- `click_element(text=None, resource_id=None)` - Click theo text HOẶC resource_id
- `long_click_element(text=None, resource_id=None)` - Long click
- `set_element_text(text=None, input_text="...", resource_id=None)` 
  ⚠️ CHÚ Ý: `text` là text của element để TÌM, `input_text` là nội dung NHẬP VÀO
- `wait_element(text=None, resource_id=None, timeout=10)` - Đợi element xuất hiện
- `scroll_to_element(text)` - Scroll tìm element

### Input
- `type_text(text)` - Gõ từng ký tự (chậm, dùng cho search suggestions)
- `send_keys(text)` - Gửi text nhanh
- `clear_text()` - Xóa text hiện tại

### Navigation  
- `press(x, y)` - Tap tọa độ (chỉ dùng khi không tìm được element)
- `press_back()` - Nhấn nút Back
- `press_home()` - Về Home
- `swipe(start_x, start_y, end_x, end_y)` - Vuốt

### System
- `set_clipboard(text)` - Copy text vào clipboard
- `get_ui_elements_info()` - Lấy danh sách UI elements

## OUTPUT FORMAT
Bạn PHẢI trả về JSON theo format sau (KHÔNG có text nào khác):

```json
{
  "goal": "Mô tả mục tiêu cuối cùng",
  "steps": [
    {
      "step": 1,
      "action": "Tên hành động ngắn gọn",
      "reasoning": "Tại sao cần làm bước này",
      "tool_hint": "tool_name(param1=value1, param2=value2)"
    }
  ]
}
```

## QUY TẮC
1. Tối đa 6-8 bước cho mỗi task
2. Mỗi bước phải là hành động cụ thể
3. Luôn bắt đầu bằng `app_start` nếu chưa mở app
4. Dùng `wait_element` sau khi mở app hoặc chuyển màn hình
5. ƯU TIÊN dùng `text` thay vì `resource_id` (dễ hơn)
6. Dùng `set_element_text(text="...", input_text="nội dung")` để nhập text
7. KHÔNG nói gì ngoài JSON

## PACKAGES PHỔ BIẾN
- Facebook: `com.facebook.katana`
- Messenger: `com.facebook.orca`  
- Zalo: `com.zing.zalo`
- Instagram: `com.instagram.android`
- YouTube: `com.google.android.youtube`
- Chrome: `com.android.chrome`
- Settings: `com.android.settings`

## VÍ DỤ
User: "Vào Facebook đăng 'Hello World'"

```json
{
  "goal": "Đăng status 'Hello World' lên Facebook",
  "steps": [
    {
      "step": 1,
      "action": "Mở ứng dụng Facebook",
      "reasoning": "Cần truy cập vào app trước khi thao tác",
      "tool_hint": "app_start(package_name='com.facebook.katana')"
    },
    {
      "step": 2,
      "action": "Đợi trang chủ load xong",
      "reasoning": "Đảm bảo UI elements đã sẵn sàng",
      "tool_hint": "wait_element(text='Bạn đang nghĩ gì?')"
    },
    {
      "step": 3,
      "action": "Click vào ô tạo status",
      "reasoning": "Mở form viết status mới",
      "tool_hint": "click_element(text='Bạn đang nghĩ gì?')"
    },
    {
      "step": 4,
      "action": "Nhập nội dung 'Hello World'",
      "reasoning": "Điền nội dung User yêu cầu",
      "tool_hint": "set_element_text(text='Bạn đang nghĩ gì?', input_text='Hello World')"
    },
    {
      "step": 5,
      "action": "Nhấn nút Đăng",
      "reasoning": "Hoàn tất đăng bài",
      "tool_hint": "click_element(text='Đăng')"
    }
  ]
}
```
"""


class PlannerBrain:
    """
    Planner Brain for generating execution plans.
    
    This is the "strategist" in the Planner-Navigator architecture.
    It generates a JSON plan that the Navigator will execute step-by-step.
    """
    
    def __init__(
        self, 
        api_key: str = None,
        model_name: str = "gemini-2.5-pro",  # Use high-capability model
        base_url: str = "http://localhost:8317/v1"
    ):
        self.api_key = api_key or os.getenv("CLIPROXY_API_KEY", "gemaauto")
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        
        print(f"🧠 Planner initialized with {model_name}")
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _get_image_media_type(self, image_path: str) -> str:
        """Get media type from image extension."""
        ext = Path(image_path).suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return media_types.get(ext, "image/png")
    
    def create_plan(
        self, 
        user_request: str,
        screenshot_path: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate an execution plan for the given request.
        
        Args:
            user_request: What the user wants to accomplish
            screenshot_path: Optional current screen state
            context: Additional context (e.g., previous actions)
            
        Returns:
            Dict with 'goal' and 'steps' list, or error
        """
        try:
            # Build message content
            user_content = []
            
            # Add screenshot if available
            if screenshot_path and Path(screenshot_path).exists():
                image_data = self._encode_image(screenshot_path)
                media_type = self._get_image_media_type(screenshot_path)
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_data}"
                    }
                })
                print(f"🧠 Planner analyzing: {screenshot_path}")
            
            # Add context and request
            prompt = f"""Nhiệm vụ: {user_request}

{f'Ngữ cảnh: {context}' if context else ''}

Hãy tạo kế hoạch thực hiện nhiệm vụ trên. Trả về JSON theo format đã chỉ định."""
            
            user_content.append({
                "type": "text",
                "text": prompt
            })
            
            # Prepare messages
            messages = [
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ]
            
            # Call API
            response = self._call_api(messages)
            
            if not response:
                return {"error": "API call failed", "steps": []}
            
            # Extract content
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse JSON from response
            plan = self._parse_plan_json(content)
            
            if plan:
                print(f"🧠 Plan created: {len(plan.get('steps', []))} steps")
                return plan
            else:
                return {"error": "Failed to parse plan", "raw": content, "steps": []}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e), "steps": []}
    
    def _parse_plan_json(self, content: str) -> Optional[Dict]:
        """Extract and parse JSON from response content."""
        # Try direct JSON parse first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in code block
        import re
        
        # Match ```json ... ``` or ``` ... ```
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON object
        json_match = re.search(r'\{[^{}]*"steps"\s*:\s*\[.*?\]\s*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _call_api(self, messages: list) -> Optional[dict]:
        """Make API call to CLIProxyAPI."""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.3  # Lower temperature for consistent planning
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Planner API Error: {e}")
            return None

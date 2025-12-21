# Gemma Android Automation

🤖 Android Automation Agent powered by Ollama (Gemma/LLaMA models)

## Features

- **48 automation tools** for Android device control
- **Agentic workflow**: PLAN → EXECUTE → VERIFY → REPORT
- **Modern GUI** with CustomTkinter
- **Multi-model support**: gemma3:12b, gemma3:4b, qwen2.5:7b
- **Vietnamese language support**

## Tools Available

| Category | Tools |
|----------|-------|
| **App Management** | app_start, app_stop, app_clear, app_current, app_info, app_list |
| **Navigation** | press, long_press, press_back, press_home, open_app |
| **Input** | type_text, swipe, scroll_element, send_keys, clear_text |
| **Screen** | take_screenshot, get_ui_elements_info |
| **Elements** | click_element, wait_element, xpath_click, scroll_to_element |
| **Gestures** | double_click, drag, pinch_in, pinch_out, swipe_points |
| **System** | screen_on/off, unlock, clipboard, hide_keyboard, shell |
| **Recording** | record_video, stop_video |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode
```bash
python gui.py
```

### CLI Mode
```bash
python app.py
```

## Requirements

- Python 3.10+
- Ollama with gemma3:12b model
- Android device connected via ADB
- uiautomator2

## Project Structure

```
├── agent/          # AI agent logic
│   ├── model.py    # GemmaAgent with tool calling
│   ├── executor.py # Tool execution
│   └── prompts.py  # System prompts
├── tools/          # 48 automation tools
│   ├── apps.py     # App management
│   ├── navigation.py
│   ├── elements.py # UI element interactions
│   ├── gestures.py
│   ├── system.py
│   └── ...
├── core/           # Core utilities
├── gui.py          # CustomTkinter GUI
├── app.py          # CLI entry point
└── config.py       # Configuration
```

## License

MIT

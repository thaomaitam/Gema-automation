"""
Gemma Android Automation Configuration
"""
import os

# ============================================================
# Model Configuration
# ============================================================
DEFAULT_MODEL = "gemma3:12b"  # Larger model = better understanding
AVAILABLE_MODELS = [
    "gemma3:12b",   # Best - 12B params
    "gemma3:4b",    # Fast - 4B params
    "gemma3:1b",    # Fastest - 1B params
    "gemma2:9b",
    "llama3.2:latest",
    "qwen2.5:7b",   # Good for tool calling
]

# ============================================================
# Paths Configuration  
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "ss")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

# Ensure directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

# ============================================================
# Android Interactive Element Classes
# ============================================================
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

SCROLLABLE_CLASSES = [
    "android.widget.ScrollView",
    "android.widget.HorizontalScrollView",
    "android.support.v7.widget.RecyclerView",
    "androidx.recyclerview.widget.RecyclerView",
    "android.widget.ListView",
    "android.widget.GridView",
    "androidx.viewpager.widget.ViewPager",
    "androidx.viewpager2.widget.ViewPager2"
]

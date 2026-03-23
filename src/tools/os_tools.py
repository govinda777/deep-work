import os
import sys
from unittest.mock import MagicMock

# Handle headless/CI environments where pyautogui might fail to import or run
try:
    if 'DISPLAY' not in os.environ and sys.platform != 'win32' and sys.platform != 'darwin':
        raise ImportError("No display detected")
    import pyautogui
except ImportError:
    print("PyAutoGUI could not be initialized (likely headless environment). Mocking for compatibility.")
    pyautogui = MagicMock()
    sys.modules["pyautogui"] = pyautogui

class OSTools:
    """
    OS automation tools using PyAutoGUI.
    """
    def __init__(self):
        # Prevent PyAutoGUI from crashing if it fails to find an element
        pyautogui.FAILSAFE = True

    def click_at(self, x: int, y: int):
        pyautogui.click(x, y)
        return f"Clicked at coordinates ({x}, {y})"

    def double_click_at(self, x: int, y: int):
        pyautogui.doubleClick(x, y)
        return f"Double clicked at coordinates ({x}, {y})"

    def type_keys(self, text: str):
        pyautogui.typewrite(text)
        return f"Typed: {text}"

    def get_screen_size(self):
        return pyautogui.size()

    def take_os_screenshot(self, path="os_screenshot.png"):
        pyautogui.screenshot(path)
        return f"OS screenshot saved to {path}"

    def press_key(self, key: str):
        pyautogui.press(key)
        return f"Pressed key: {key}"

    def drag_to(self, x: int, y: int):
        pyautogui.dragTo(x, y)
        return f"Dragged to coordinates ({x}, {y})"

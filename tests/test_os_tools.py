import unittest
from unittest.mock import MagicMock, patch
from src.tools.os_tools import OSTools
import os

class TestOSTools(unittest.TestCase):
    @patch('src.tools.os_tools.pyautogui')
    def test_click_at(self, mock_pyautogui):
        tools = OSTools()
        result = tools.click_at(100, 200)
        self.assertEqual(result, "Clicked at coordinates (100, 200)")
        mock_pyautogui.click.assert_called_once_with(100, 200)

    @patch('src.tools.os_tools.pyautogui')
    def test_double_click_at(self, mock_pyautogui):
        tools = OSTools()
        result = tools.double_click_at(100, 200)
        self.assertEqual(result, "Double-clicked at coordinates (100, 200)")
        mock_pyautogui.doubleClick.assert_called_once_with(100, 200)

    @patch('src.tools.os_tools.pyautogui')
    def test_type_keys(self, mock_pyautogui):
        tools = OSTools()
        result = tools.type_keys("Hello World")
        self.assertEqual(result, "Typed: Hello World")
        mock_pyautogui.typewrite.assert_called_once_with("Hello World")

    @patch('src.tools.os_tools.pyautogui')
    def test_get_screen_size(self, mock_pyautogui):
        mock_pyautogui.size.return_value = (1920, 1080)
        tools = OSTools()
        size = tools.get_screen_size()
        self.assertEqual(size, (1920, 1080))
        mock_pyautogui.size.assert_called_once()

    @patch('src.tools.os_tools.pyautogui')
    def test_take_os_screenshot(self, mock_pyautogui):
        tools = OSTools()
        result = tools.take_os_screenshot("test_os.png")
        self.assertEqual(result, "OS screenshot saved to test_os.png")
        mock_pyautogui.screenshot.assert_called_once_with("test_os.png")

    @patch('src.tools.os_tools.pyautogui')
    def test_press_key(self, mock_pyautogui):
        tools = OSTools()
        result = tools.press_key("enter")
        self.assertEqual(result, "Pressed key: enter")
        mock_pyautogui.press.assert_called_once_with("enter")

    @patch('src.tools.os_tools.pyautogui')
    def test_drag_to(self, mock_pyautogui):
        tools = OSTools()
        result = tools.drag_to(300, 400)
        self.assertEqual(result, "Dragged to coordinates (300, 400)")
        mock_pyautogui.dragTo.assert_called_once_with(300, 400)

if __name__ == '__main__':
    unittest.main()

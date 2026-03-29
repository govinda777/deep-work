import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.tools.browser_tools import BrowserTools
import os

class TestBrowserTools(unittest.IsolatedAsyncioTestCase):
    @patch('src.tools.browser_tools.async_playwright')
    async def test_navigate(self, mock_playwright):
        mock_pw_context_manager = mock_playwright.return_value
        mock_pw_context_manager.start = AsyncMock()
        mock_pw_instance = mock_pw_context_manager.start.return_value

        mock_browser = mock_pw_instance.chromium.launch = AsyncMock()
        mock_browser_instance = mock_browser.return_value

        mock_context = mock_browser_instance.new_context = AsyncMock()
        mock_context_instance = mock_context.return_value

        mock_page = mock_context_instance.new_page = AsyncMock()
        mock_page_instance = mock_page.return_value
        mock_page_instance.goto = AsyncMock()

        tools = BrowserTools()
        tools.page = mock_page_instance

        result = await tools.navigate("https://example.com")
        self.assertEqual(result, "Navigated to https://example.com")
        mock_page_instance.goto.assert_called_once_with("https://example.com", wait_until="networkidle")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_click_element(self, mock_playwright):
        tools = BrowserTools()
        mock_page = AsyncMock()
        tools.page = mock_page
        result = await tools.click_element("#login")
        self.assertEqual(result, "Clicked element #login")
        mock_page.click.assert_called_once_with("#login")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_input_text(self, mock_playwright):
        tools = BrowserTools()
        mock_page = AsyncMock()
        tools.page = mock_page
        result = await tools.input_text("#user", "testuser")
        self.assertEqual(result, "Entered text into #user")
        mock_page.fill.assert_called_once_with("#user", "testuser")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_hover(self, mock_playwright):
        tools = BrowserTools()
        mock_page = AsyncMock()
        tools.page = mock_page
        result = await tools.hover("#menu")
        self.assertEqual(result, "Hovered over element #menu")
        mock_page.hover.assert_called_once_with("#menu")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_double_click(self, mock_playwright):
        tools = BrowserTools()
        mock_page = AsyncMock()
        tools.page = mock_page
        result = await tools.double_click("#button")
        self.assertEqual(result, "Double-clicked element #button")
        mock_page.dblclick.assert_called_once_with("#button")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_scroll(self, mock_playwright):
        tools = BrowserTools()
        mock_page = AsyncMock()
        tools.page = mock_page
        result = await tools.scroll("down", 500)
        self.assertEqual(result, "Scrolled down by 500 pixels")
        mock_page.evaluate.assert_called_once_with("window.scrollBy(0, 500)")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_get_page_content(self, mock_playwright):
        tools = BrowserTools()
        mock_page = AsyncMock()
        mock_page.content.return_value = "<html>Content</html>"
        tools.page = mock_page
        content = await tools.get_page_content()
        self.assertEqual(content, "<html>Content</html>")

    @patch('src.tools.browser_tools.async_playwright')
    async def test_session_persistence(self, mock_playwright):
        mock_pw_context_manager = mock_playwright.return_value
        mock_pw_context_manager.start = AsyncMock()
        mock_pw_instance = mock_pw_context_manager.start.return_value
        mock_browser = mock_pw_instance.chromium.launch = AsyncMock()
        mock_browser_instance = mock_browser.return_value
        mock_context = mock_browser_instance.new_context = AsyncMock()
        mock_context_instance = mock_context.return_value
        mock_page = mock_context_instance.new_page = AsyncMock()

        session_file = "test_session.json"
        if os.path.exists(session_file):
            os.remove(session_file)

        tools = BrowserTools(session_file=session_file)

        # Test start browser without session file
        await tools.start_browser()
        mock_browser_instance.new_context.assert_called_once()
        self.assertIsNone(mock_browser_instance.new_context.call_args.kwargs.get('storage_state'))

        # Test stop browser (should save session)
        mock_context_instance.storage_state = AsyncMock()
        await tools.stop_browser()
        mock_context_instance.storage_state.assert_called_once_with(path=session_file)

        # Manually create the file to simulate it exists
        with open(session_file, 'w') as f:
            f.write('{"cookies": []}')

        # Test start browser with session file
        await tools.start_browser()
        self.assertEqual(mock_browser_instance.new_context.call_args_list[-1].kwargs.get('storage_state'), session_file)

        if os.path.exists(session_file):
            os.remove(session_file)

if __name__ == '__main__':
    unittest.main()

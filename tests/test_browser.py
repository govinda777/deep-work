import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.tools.browser_tools import BrowserTools

class TestBrowserTools(unittest.IsolatedAsyncioTestCase):
    @patch('src.tools.browser_tools.async_playwright')
    async def test_navigate(self, mock_playwright):
        # Setup mocks
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
        # We need to manually set the page to avoid the start_browser call if it's too complex to mock
        tools.page = mock_page_instance

        result = await tools.navigate("https://example.com")

        self.assertEqual(result, "Navigated to https://example.com")
        mock_page_instance.goto.assert_called_once_with("https://example.com")

if __name__ == '__main__':
    unittest.main()

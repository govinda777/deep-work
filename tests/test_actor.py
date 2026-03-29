import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.actor import Actor

class TestActor(unittest.IsolatedAsyncioTestCase):
    @patch('src.agents.actor.BrowserTools')
    @patch('src.agents.actor.OSTools')
    async def test_execute_browser_task(self, mock_os, mock_browser):
        mock_browser_instance = mock_browser.return_value
        mock_browser_instance.navigate = AsyncMock(return_value="Navigated")

        actor = Actor()
        # Ensure it uses the mock instance
        actor.browser_tools = mock_browser_instance

        task = MagicMock()
        task.tool_type = "browser"
        task.action = "navigate"
        task.parameters = {"url": "http://example.com"}

        result = await actor.execute_task(task)
        self.assertEqual(result, "Navigated")
        mock_browser_instance.navigate.assert_awaited_once_with(url="http://example.com")

    @patch('src.agents.actor.BrowserTools')
    @patch('src.agents.actor.OSTools')
    async def test_execute_os_task(self, mock_os, mock_browser):
        mock_os_instance = mock_os.return_value
        mock_os_instance.click_at = MagicMock(return_value="Clicked")

        actor = Actor()
        actor.os_tools = mock_os_instance

        task = MagicMock()
        task.tool_type = "os"
        task.action = "click_at"
        task.parameters = {"x": 10, "y": 20}

        result = await actor.execute_task(task)
        self.assertEqual(result, "Clicked")
        mock_os_instance.click_at.assert_called_once_with(x=10, y=20)

    @patch('src.agents.actor.BrowserTools')
    @patch('src.agents.actor.OSTools')
    async def test_unknown_tool_type(self, mock_os, mock_browser):
        actor = Actor()
        task = MagicMock()
        task.tool_type = "unknown"
        result = await actor.execute_task(task)
        self.assertIn("Unknown tool type", result)

if __name__ == '__main__':
    unittest.main()

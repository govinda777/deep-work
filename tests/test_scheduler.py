import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.agents.scheduler import TaskScheduler

class TestTaskScheduler(unittest.IsolatedAsyncioTestCase):
    @patch('src.agents.orchestrator.Orchestrator')
    async def test_schedule_once(self, mock_orchestrator):
        mock_orchestrator_instance = mock_orchestrator.return_value
        mock_orchestrator_instance.run = AsyncMock()

        scheduler = TaskScheduler(mock_orchestrator_instance)

        # Test scheduling once with a very small delay
        task = await scheduler.schedule_once("test goal", 0.1)

        # Wait for the task to complete
        await asyncio.sleep(0.2)

        mock_orchestrator_instance.run.assert_awaited_once_with("test goal")

    @patch('src.agents.orchestrator.Orchestrator')
    async def test_schedule_periodic(self, mock_orchestrator):
        mock_orchestrator_instance = mock_orchestrator.return_value
        mock_orchestrator_instance.run = AsyncMock()

        scheduler = TaskScheduler(mock_orchestrator_instance)

        # Test scheduling periodic with a very small interval
        task = await scheduler.schedule_periodic("test goal", 0.1)

        # Wait for two intervals
        await asyncio.sleep(0.25)

        # Should have run at least twice (immediate=True)
        self.assertGreaterEqual(mock_orchestrator_instance.run.call_count, 2)

        scheduler.stop_all()
        await asyncio.sleep(0.1) # Wait for cancellation to take effect

if __name__ == '__main__':
    unittest.main()

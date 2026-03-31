import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.orchestrator import Orchestrator

class TestOrchestrator(unittest.IsolatedAsyncioTestCase):
    @patch('src.agents.orchestrator.Planner')
    @patch('src.agents.orchestrator.Actor')
    @patch('src.agents.orchestrator.Validator')
    @patch('src.agents.orchestrator.WorkflowSynthesizer')
    @patch('src.memory.pinecone_manager.MemoryManager')
    async def test_run_goal(self, mock_memory, mock_synthesizer, mock_validator, mock_actor, mock_planner):
        # Setup mocks
        mock_memory_instance = mock_memory.return_value
        mock_memory_instance.asearch_memory = AsyncMock(return_value=[])
        mock_memory_instance.aadd_memory = AsyncMock()

        mock_planner_instance = mock_planner.return_value
        mock_task = MagicMock()
        mock_task.description = "Test Task"
        mock_task.tool_type = "browser"
        mock_task.action = "navigate"
        mock_task.parameters = {"url": "http://test.com"}
        mock_task.expected_outcome = "Page loaded"

        mock_plan = MagicMock()
        mock_plan.tasks = [mock_task]
        mock_planner_instance.plan.return_value = mock_plan

        mock_actor_instance = mock_actor.return_value
        mock_actor_instance.execute_task = AsyncMock(return_value="Success")
        mock_actor_instance.browser_tools = MagicMock()
        mock_actor_instance.browser_tools.stop_browser = AsyncMock()
        mock_actor_instance.browser_tools.get_page_summary = AsyncMock(return_value="Summary")
        mock_actor_instance.browser_tools.get_screenshot_base64 = AsyncMock(return_value="base64")

        mock_validator_instance = mock_validator.return_value
        mock_validation = MagicMock()
        mock_validation.is_successful = True
        mock_validator_instance.validate_action.return_value = mock_validation

        mock_synthesizer_instance = mock_synthesizer.return_value
        mock_synthesizer_instance.aget_workflow = AsyncMock(return_value=None)
        mock_synthesizer_instance.asave_workflow = AsyncMock()

        orchestrator = Orchestrator(mock_memory_instance)
        # Manually inject mocks
        orchestrator.planner = mock_planner_instance
        orchestrator.actor = mock_actor_instance
        orchestrator.validator = mock_validator_instance
        orchestrator.synthesizer = mock_synthesizer_instance

        await orchestrator.run("Test Goal")

        mock_planner_instance.plan.assert_called_once()
        mock_actor_instance.execute_task.assert_awaited_once_with(mock_task)
        mock_validator_instance.validate_action.assert_called_once()
        mock_synthesizer_instance.asave_workflow.assert_awaited_once()

if __name__ == '__main__':
    unittest.main()

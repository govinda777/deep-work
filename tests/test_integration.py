import asyncio
import unittest
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Mock pyautogui before importing anything that uses it
import sys
sys.modules['pyautogui'] = MagicMock()

from src.agents.orchestrator import Orchestrator
from src.agents.planner import Plan, Task
from src.agents.validator import ValidationResult

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    @patch('src.agents.orchestrator.Planner')
    @patch('src.agents.orchestrator.Actor')
    @patch('src.agents.orchestrator.Validator')
    @patch('src.agents.orchestrator.MemoryManager')
    async def test_full_run_success(self, mock_memory_mgr, mock_validator, mock_actor, mock_planner):
        # Setup mocks
        memory_instance = mock_memory_mgr.return_value
        planner_instance = mock_planner.return_value
        actor_instance = mock_actor.return_value
        validator_instance = mock_validator.return_value

        # Mock Plan
        mock_plan = Plan(tasks=[
            Task(description="Navigate to Google", expected_outcome="Google page loaded", tool_type="browser", parameters={"url": "https://google.com"}),
            Task(description="Search for Deep-Work", expected_outcome="Search results shown", tool_type="browser", parameters={"selector": "input[name='q']", "text": "Deep-Work"})
        ])
        planner_instance.plan.return_value = mock_plan

        # Mock Actor
        actor_instance.execute_task = AsyncMock(side_effect=["Navigated", "Typed"])
        actor_instance.browser_tools.get_page_content = AsyncMock(return_value="<html>Google</html>")

        # Mock Validator
        validator_instance.validate_action.return_value = ValidationResult(is_successful=True, feedback="Great job")

        # Initialize Orchestrator
        orchestrator = Orchestrator(memory=memory_instance)

        # Run
        goal = "Search for Deep-Work on Google"
        final_state = await orchestrator.run(goal)

        # Assertions
        self.assertEqual(len(final_state['results']), 2)
        self.assertEqual(final_state['current_task_index'], 2)
        planner_instance.plan.assert_called_once_with(goal)
        self.assertEqual(actor_instance.execute_task.call_count, 2)
        self.assertEqual(validator_instance.validate_action.call_count, 2)
        self.assertEqual(memory_instance.add_memory.call_count, 3) # 1 for plan, 2 for execution

    @patch('src.agents.orchestrator.Planner')
    @patch('src.agents.orchestrator.Actor')
    @patch('src.agents.orchestrator.Validator')
    @patch('src.agents.orchestrator.MemoryManager')
    async def test_full_run_with_retry(self, mock_memory_mgr, mock_validator, mock_actor, mock_planner):
        # Setup mocks
        memory_instance = mock_memory_mgr.return_value
        planner_instance = mock_planner.return_value
        actor_instance = mock_actor.return_value
        validator_instance = mock_validator.return_value

        # Mock Plan
        mock_plan = Plan(tasks=[
            Task(description="Navigate to Google", expected_outcome="Google page loaded", tool_type="browser", parameters={"url": "https://google.com"})
        ])
        planner_instance.plan.return_value = mock_plan

        # Mock Actor
        actor_instance.execute_task = AsyncMock(return_value="Action performed")
        actor_instance.browser_tools.get_page_content = AsyncMock(return_value="Content")

        # Mock Validator: first fail then success
        validator_instance.validate_action.side_effect = [
            ValidationResult(is_successful=False, feedback="Failed first time"),
            ValidationResult(is_successful=True, feedback="Success second time")
        ]

        # Initialize Orchestrator
        orchestrator = Orchestrator(memory=memory_instance)

        # Run
        final_state = await orchestrator.run("Goal")

        # Assertions
        self.assertEqual(final_state['retries'], 0) # reset on success
        self.assertEqual(final_state['current_task_index'], 1)
        self.assertEqual(actor_instance.execute_task.call_count, 2) # executed twice due to retry
        self.assertEqual(validator_instance.validate_action.call_count, 2)
        self.assertEqual(memory_instance.add_memory.call_count, 4) # 1 plan, 2 execution, 1 failure log

if __name__ == '__main__':
    unittest.main()

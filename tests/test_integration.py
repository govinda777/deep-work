import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.orchestrator import Orchestrator
from src.agents.planner import Plan, Task
from src.agents.validator import ValidationResult

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    @patch('src.agents.orchestrator.Planner')
    @patch('src.agents.orchestrator.Actor')
    @patch('src.agents.orchestrator.Validator')
    @patch('src.memory.pinecone_manager.MemoryManager')
    async def test_orchestrator_run(self, mock_memory, mock_validator, mock_actor, mock_planner):
        # Mocking Planner.plan
        mock_planner_instance = mock_planner.return_value
        mock_planner_instance.plan.return_value = Plan(tasks=[
            Task(description="Navigate to Google", tool_type="browser", parameters={"url": "https://google.com"}),
            Task(description="Search for Deep-Work", tool_type="browser", parameters={"selector": "input[name='q']", "text": "Deep-Work"})
        ])

        # Mocking Actor.execute_task
        mock_actor_instance = mock_actor.return_value
        mock_actor_instance.execute_task = AsyncMock(side_effect=["Navigated to Google", "Entered text into input[name='q']"])
        mock_actor_instance.browser_tools = AsyncMock()
        mock_actor_instance.browser_tools.get_page_content.return_value = "<html>Google</html>"

        # Mocking Validator.validate_action
        mock_validator_instance = mock_validator.return_value
        mock_validator_instance.validate_action.return_value = ValidationResult(is_successful=True, feedback="Success")

        # Initialize Orchestrator with mock memory
        orchestrator = Orchestrator(memory=mock_memory)

        # Run the orchestrator
        final_state = await orchestrator.run("Search Google for Deep-Work")

        # Assertions
        self.assertEqual(len(final_state['results']), 2)
        self.assertEqual(final_state['current_task_index'], 2)
        mock_planner_instance.plan.assert_called_once_with("Search Google for Deep-Work")
        self.assertEqual(mock_actor_instance.execute_task.call_count, 2)
        self.assertEqual(mock_validator_instance.validate_action.call_count, 2)
        self.assertEqual(mock_memory.add_memory.call_count, 3) # 1 plan + 2 executions

if __name__ == '__main__':
    unittest.main()

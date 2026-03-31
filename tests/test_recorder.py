import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import json
from src.agents.recorder import WorkflowSynthesizer

class TestWorkflowSynthesizer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_memory = MagicMock()
        self.mock_memory.aadd_memory = AsyncMock()
        self.mock_memory.asearch_memory = AsyncMock()
        self.synthesizer = WorkflowSynthesizer(self.mock_memory)

    def test_save_workflow(self):
        mock_task = MagicMock()
        mock_task.description = "Task 1"
        mock_task.model_dump.return_value = {"description": "Task 1"}

        self.synthesizer.save_workflow("Test Goal", [mock_task])

        self.mock_memory.add_memory.assert_called_once()
        args, kwargs = self.mock_memory.add_memory.call_args
        self.assertIn("Workflow for 'Test Goal'", args[0])
        metadata = args[1] if len(args) > 1 else kwargs.get('metadata')
        self.assertEqual(metadata['goal'], "Test Goal")
        self.assertEqual(metadata['type'], "workflow")
        self.assertIn('"description": "Task 1"', metadata['tasks_json'])

    async def test_asave_workflow(self):
        mock_task = MagicMock()
        mock_task.description = "Task 1"
        mock_task.model_dump.return_value = {"description": "Task 1"}

        await self.synthesizer.asave_workflow("Test Goal", [mock_task])

        self.mock_memory.aadd_memory.assert_awaited_once()
        args, kwargs = self.mock_memory.aadd_memory.call_args
        self.assertIn("Workflow for 'Test Goal'", args[0])
        metadata = args[1] if len(args) > 1 else kwargs.get('metadata')
        self.assertEqual(metadata['goal'], "Test Goal")
        self.assertIn('"description": "Task 1"', metadata['tasks_json'])

    async def test_aget_workflow_found(self):
        mock_result = MagicMock()
        mock_result.metadata = {
            "type": "workflow",
            "tasks_json": json.dumps([{"description": "Task 1"}])
        }
        self.mock_memory.asearch_memory.return_value = [mock_result]

        workflow = await self.synthesizer.aget_workflow("Test Goal")

        self.assertEqual(len(workflow), 1)
        self.assertEqual(workflow[0]['description'], "Task 1")
        self.mock_memory.asearch_memory.assert_awaited_once_with("Test Goal", k=1)

    async def test_aget_workflow_not_found(self):
        self.mock_memory.asearch_memory.return_value = []
        workflow = await self.synthesizer.aget_workflow("Nonexistent")
        self.assertIsNone(workflow)

if __name__ == '__main__':
    unittest.main()

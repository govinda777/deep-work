from typing import List
from src.agents.planner import Task
from src.memory.pinecone_manager import MemoryManager
import json

class WorkflowSynthesizer:
    """
    Synthesizes successful task sequences into reusable workflows stored in memory.
    """
    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def save_workflow(self, goal: str, tasks: List[Task]):
        """
        Saves a sequence of tasks that successfully achieved a goal.
        """
        # Convert tasks to a serializable format
        serialized_tasks = [task.model_dump() for task in tasks]

        workflow_summary = f"Workflow for '{goal}':\n" + "\n".join([f"{i+1}. {t.description}" for i, t in enumerate(tasks)])

        metadata = {
            "type": "workflow",
            "goal": goal,
            "tasks_json": json.dumps(serialized_tasks)
        }

        self.memory.add_memory(workflow_summary, metadata)
        print(f"Workflow for '{goal}' synthesized and saved to memory.")

    async def asave_workflow(self, goal: str, tasks: List[Task]):
        """
        Saves a sequence of tasks that successfully achieved a goal asynchronously.
        """
        serialized_tasks = [task.model_dump() for task in tasks]
        workflow_summary = f"Workflow for '{goal}':\n" + "\n".join([f"{i+1}. {t.description}" for i, t in enumerate(tasks)])

        metadata = {
            "type": "workflow",
            "goal": goal,
            "tasks_json": json.dumps(serialized_tasks)
        }

        await self.memory.aadd_memory(workflow_summary, metadata)
        print(f"Workflow for '{goal}' synthesized and saved to memory (async).")

    def get_workflow(self, goal_query: str):
        """
        Retrieves a similar past workflow from memory.
        """
        results = self.memory.search_memory(goal_query, k=1)
        for res in results:
            if res.metadata.get("type") == "workflow":
                return json.loads(res.metadata.get("tasks_json"))
        return None

    async def aget_workflow(self, goal_query: str):
        """
        Retrieves a similar past workflow from memory asynchronously.
        """
        results = await self.memory.asearch_memory(goal_query, k=1)
        for res in results:
            if res.metadata.get("type") == "workflow":
                return json.loads(res.metadata.get("tasks_json"))
        return None

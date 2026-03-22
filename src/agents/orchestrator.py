from typing import TypedDict, List, Annotated, Sequence
from langgraph.graph import StateGraph, END
from src.agents.planner import Planner, Plan, Task
from src.agents.actor import Actor
from src.agents.validator import Validator
from src.memory.pinecone_manager import MemoryManager
import asyncio

class AgentState(TypedDict):
    goal: str
    plan: List[Task]
    current_task_index: int
    results: List[str]
    memory: MemoryManager
    finished: bool
    retries: int

class Orchestrator:
    """
    Orchestrates the lifecycle of the Deep-Work agent using LangGraph.
    """
    def __init__(self, memory: MemoryManager):
        self.planner = Planner()
        self.actor = Actor()
        self.validator = Validator()
        self.memory = memory
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("validate", self._validate_node)

        # Edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")

        workflow.add_conditional_edges(
            "validate",
            self._should_continue,
            {
                "continue": "execute",
                "end": END,
                "retry": "execute"
            }
        )

        workflow.add_edge("execute", "validate")

        return workflow.compile()

    def _plan_node(self, state: AgentState):
        print(f"Planning for goal: {state['goal']}")
        plan = self.planner.plan(state['goal'])
        # Store plan in memory
        self.memory.add_memory(f"Created plan for goal: {state['goal']}", {"type": "plan", "goal": state['goal']})
        return {"plan": plan.tasks, "current_task_index": 0, "results": [], "retries": 0}

    async def _execute_node(self, state: AgentState):
        task = state['plan'][state['current_task_index']]
        print(f"Executing task {state['current_task_index'] + 1}/{len(state['plan'])}: {task.description}")
        result = await self.actor.execute_task(task)
        # Store execution result in memory
        self.memory.add_memory(f"Executed task: {task.description}. Result: {result}", {"type": "execution", "task": task.description})
        return {"results": state['results'] + [result]}

    async def _validate_node(self, state: AgentState):
        task = state['plan'][state['current_task_index']]
        last_result = state['results'][-1]

        # In a real scenario, we'd get the actual page content from the actor's browser tools
        page_content = await self.actor.browser_tools.get_page_content() if task.tool_type == 'browser' else "OS State not readable directly"

        validation = self.validator.validate_action(
            action_description=task.description,
            intended_outcome=task.expected_outcome,
            page_content=page_content
        )

        print(f"Validation for task {state['current_task_index'] + 1}: {'Success' if validation.is_successful else 'Failure'}")

        if validation.is_successful:
            return {"current_task_index": state['current_task_index'] + 1, "retries": 0}
        else:
            print(f"Validation failed. Feedback: {validation.feedback}")
            return {"retries": state['retries'] + 1}

    def _should_continue(self, state: AgentState):
        if state['current_task_index'] >= len(state['plan']):
            return "end"
        if state['retries'] > 3:
            print("Max retries reached. Stopping.")
            return "end"
        return "continue"

    async def run(self, goal: str):
        initial_state = {
            "goal": goal,
            "plan": [],
            "current_task_index": 0,
            "results": [],
            "memory": self.memory,
            "finished": False,
            "retries": 0
        }
        try:
            result = await self.graph.ainvoke(initial_state)
            return result
        finally:
            await self.actor.browser_tools.stop_browser()

from typing import TypedDict, List, Annotated, Sequence
from langgraph.graph import StateGraph, END
from src.agents.planner import Planner, Plan, Task
from src.agents.actor import Actor
from src.agents.validator import Validator
from src.agents.recorder import WorkflowSynthesizer
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
        self.synthesizer = WorkflowSynthesizer(memory)
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
                "retry": "execute",
                "replan": "plan"
            }
        )

        workflow.add_edge("execute", "validate")

        return workflow.compile()

    def _plan_node(self, state: AgentState):
        print(f"Planning for goal: {state['goal']}")

        # Retrieve context from memory
        relevant_memories = self.memory.search_memory(state['goal'], k=3)
        context = "\n".join([m.page_content for m in relevant_memories])

        # Add feedback from previous failed attempts if replanning
        if state.get('plan'):
            # Only if we have executed at least one task or have some failure context
            last_task_desc = state['plan'][state['current_task_index']].description if state.get('current_task_index', 0) < len(state['plan']) else "Unknown"
            last_result = state['results'][-1] if state.get('results') else "No result"
            context += f"\n\nPrevious attempt failed at task: {last_task_desc}. Result: {last_result}. Re-planning based on this failure."

        plan = self.planner.plan(state['goal'], context=context)
        # Store plan in memory
        self.memory.add_memory(f"Created plan for goal: {state['goal']}", {"type": "plan", "goal": state['goal']})

        # When replanning, we might want to keep the results of successfully completed tasks
        return {
            "plan": plan.tasks,
            "current_task_index": 0,
            "results": state.get('results', []),
            "retries": state.get('retries', 0)
        }

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

        # Get the actual page content and screenshot from the actor's browser tools
        page_content = ""
        screenshot_base64 = None
        if task.tool_type == 'browser':
            # Use get_page_summary instead of full content for efficiency
            page_content = await self.actor.browser_tools.get_page_summary()
            screenshot_base64 = await self.actor.browser_tools.get_screenshot_base64()
        else:
             page_content = "OS State not readable directly"

        validation = self.validator.validate_action(
            action_description=task.description,
            intended_outcome=task.expected_outcome,
            page_content=page_content,
            screenshot_base64=screenshot_base64
        )

        print(f"Validation for task {state['current_task_index'] + 1}: {'Success' if validation.is_successful else 'Failure'}")

        if validation.is_successful:
            return {"current_task_index": state['current_task_index'] + 1, "retries": 0}
        else:
            print(f"Validation failed. Feedback: {validation.feedback}")
            return {"retries": state['retries'] + 1}

    def _should_continue(self, state: AgentState):
        if state['current_task_index'] >= len(state['plan']):
            # Goal achieved! Synthesize workflow into memory.
            print("Goal achieved. Saving workflow to memory...")
            self.synthesizer.save_workflow(state['goal'], state['plan'])
            return "end"
        if state['retries'] >= 3:
            # If we failed multiple times, try replanning instead of giving up immediately
            print(f"Task failed {state['retries']} times. Requesting re-plan...")
            if state['retries'] > 5: # Absolute max retries including replans
                print("Max total retries reached. Stopping.")
                return "end"
            return "replan"
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
            return await self.graph.ainvoke(initial_state)
        finally:
            await self.actor.browser_tools.stop_browser()

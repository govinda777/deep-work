from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

class Task(BaseModel):
    description: str = Field(description="Granular task description")
    tool_type: str = Field(description="The tool required for the task: 'browser' or 'os'")
    action: str = Field(description="The method to be called (e.g., 'navigate', 'click_element', 'type_keys')")
    parameters: dict = Field(default_factory=dict, description="Parameters for the tool")
    expected_outcome: str = Field(description="The expected visual or state outcome after the task")

class Plan(BaseModel):
    tasks: List[Task] = Field(description="Sequential list of tasks to achieve the goal")

class Planner:
    """
    Decomposes instructions into a sequence of subtasks.
    """
    def __init__(self, model="gpt-4o"):
        self.llm = ChatOpenAI(model=model)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a task planner for a digital agent named Deep-Work. "
                       "Decompose the user's goal into a sequential list of steps using browser or OS tools. "
                       "Be precise and output the plan in a structured format.\n\n"
                       "Available Tools and Actions:\n"
                       "1. BrowserTools ('tool_type': 'browser'):\n"
                       "   - 'navigate'(url: str): Navigate to a specific URL.\n"
                       "   - 'click_element'(selector: str): Click on a DOM element.\n"
                       "   - 'input_text'(selector: str, text: str): Fill a text field.\n"
                       "   - 'hover'(selector: str): Hover over an element.\n"
                       "   - 'double_click'(selector: str): Double-click an element.\n"
                       "   - 'scroll'(direction: str, amount: int): Scroll the page ('up' or 'down').\n"
                       "   - 'take_screenshot'(path: str): Capture the browser view.\n"
                       "   - 'get_page_summary'(): Get a text summary of the page.\n"
                       "   - 'get_page_content'(): Get the full HTML content of the page.\n\n"
                       "2. OSTools ('tool_type': 'os'):\n"
                       "   - 'click_at'(x: int, y: int): Click at specific screen coordinates.\n"
                       "   - 'double_click_at'(x: int, y: int): Double-click at screen coordinates.\n"
                       "   - 'type_keys'(text: str): Type text globally.\n"
                       "   - 'press_key'(key: str): Press a specific key (e.g., 'enter', 'tab').\n"
                       "   - 'drag_to'(x: int, y: int): Drag the mouse to coordinates.\n"
                       "   - 'get_screen_size'(): Get the screen resolution.\n"
                       "   - 'take_os_screenshot'(path: str): Capture the entire screen.\n\n"
                       "Consider the retrieved context from past tasks to optimize the plan and avoid repeating mistakes.\n\n"
                       "Retrieved Context:\n{context}"),
            ("human", "{goal}")
        ])
        self.chain = self.prompt | self.llm.with_structured_output(Plan)

    def plan(self, goal: str, context: str = "") -> Plan:
        return self.chain.invoke({"goal": goal, "context": context or "No relevant past experiences found."})

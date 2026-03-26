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
                       "Be precise and output the plan in a structured format. "
                       "Consider the retrieved context from past tasks to optimize the plan and avoid repeating mistakes.\n\n"
                       "Retrieved Context:\n{context}"),
            ("human", "{goal}")
        ])
        self.chain = self.prompt | self.llm.with_structured_output(Plan)

    def plan(self, goal: str, context: str = "") -> Plan:
        return self.chain.invoke({"goal": goal, "context": context or "No relevant past experiences found."})

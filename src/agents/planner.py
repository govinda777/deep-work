from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

class Task(BaseModel):
    description: str = Field(description="Granular task description")
    expected_outcome: str = Field(description="The expected outcome of the task for validation")
    tool_type: str = Field(description="The tool required for the task: 'browser' or 'os'")
    parameters: dict = Field(default_factory=dict, description="Parameters for the tool")

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
                       "For each task, provide a clear 'description', a specific 'expected_outcome' for validation, "
                       "the 'tool_type' (browser or os), and any necessary 'parameters'. "
                       "Be precise and output the plan in a structured format."),
            ("human", "{goal}")
        ])
        self.chain = self.prompt | self.llm.with_structured_output(Plan)

    def plan(self, goal: str) -> Plan:
        return self.chain.invoke({"goal": goal})

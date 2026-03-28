from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    is_successful: bool = Field(description="True if the action achieved the desired outcome, False otherwise")
    feedback: str = Field(description="Explanation of why the action was successful or not, with suggestions for recovery.")

class Validator:
    """
    Verifies the outcome of actions using LLM reasoning.
    """
    def __init__(self, model="gpt-4o"):
        self.llm = ChatOpenAI(model=model)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a validation expert for Deep-Work. "
                       "Your goal is to verify if the last action taken by the agent "
                       "was successful by comparing the current state of the page/system "
                       "with the intended outcome. "
                       "Output your verification results in a structured format."),
            ("human", "Action: {action_description}\n"
                      "Intended outcome: {intended_outcome}\n"
                      "Current page content (partial): {page_content_summary}\n"
                      "Is this action successful?")
        ])
        self.chain = self.prompt | self.llm.with_structured_output(ValidationResult)

    def validate_action(self, action_description: str, intended_outcome: str, page_content: str, screenshot_base64: str = None) -> ValidationResult:
        # Use a summary or truncate the page content for context window efficiency
        summary = page_content[:2000] if page_content else "No content available."

        input_data = {
            "action_description": action_description,
            "intended_outcome": intended_outcome,
            "page_content_summary": summary
        }

        if screenshot_base64:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a validation expert for Deep-Work. "
                           "Your goal is to verify if the last action taken by the agent "
                           "was successful by comparing the current state of the page/system "
                           "with the intended outcome. "
                           "You have both text summary and a screenshot to evaluate the state. "
                           "Output your verification results in a structured format."),
                ("human", [
                    {"type": "text", "text": "Action: {action_description}\nIntended outcome: {intended_outcome}\nPage Summary: {page_content_summary}\nIs this action successful?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ])
            ])
            chain = prompt | self.llm.with_structured_output(ValidationResult)
            return chain.invoke(input_data)

        return self.chain.invoke(input_data)

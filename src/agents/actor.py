import asyncio
from src.tools.browser_tools import BrowserTools
from src.tools.os_tools import OSTools

class Actor:
    """
    Executes tasks using the provided tools.
    """
    def __init__(self):
        self.browser_tools = BrowserTools()
        self.os_tools = OSTools()

    async def execute_task(self, task):
        """
        Executes a single task based on the tool type and parameters.
        """
        tool_type = task.tool_type.lower()
        params = task.parameters
        description = task.description

        if tool_type == "browser":
            if "navigate" in description.lower():
                return await self.browser_tools.navigate(params.get("url"))
            elif "click" in description.lower():
                return await self.browser_tools.click_element(params.get("selector"))
            elif "input" in description.lower() or "type" in description.lower():
                return await self.browser_tools.input_text(params.get("selector"), params.get("text"))
            elif "screenshot" in description.lower():
                return await self.browser_tools.take_screenshot()
            else:
                return f"Browser tool: {description}"
        elif tool_type == "os":
            if "click" in description.lower():
                return self.os_tools.click_at(params.get("x"), params.get("y"))
            elif "type" in description.lower():
                return self.os_tools.type_keys(params.get("text"))
            elif "press" in description.lower():
                return self.os_tools.press_key(params.get("key"))
            elif "screenshot" in description.lower():
                return self.os_tools.take_os_screenshot()
            else:
                return f"OS tool: {description}"
        else:
            return f"Unknown tool type: {tool_type}"

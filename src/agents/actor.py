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
        params = task.parameters or {}
        description = task.description.lower()

        try:
            if tool_type == "browser":
                if "navigate" in description:
                    url = params.get("url")
                    if not url:
                        return "Error: Missing 'url' parameter for navigate task"
                    return await self.browser_tools.navigate(url)
                elif "click" in description:
                    selector = params.get("selector")
                    if not selector:
                        return "Error: Missing 'selector' parameter for click task"
                    return await self.browser_tools.click_element(selector)
                elif any(word in description for word in ["input", "type", "fill"]):
                    selector = params.get("selector")
                    text = params.get("text")
                    if not selector or text is None:
                        return f"Error: Missing 'selector' or 'text' parameter for input task. Params: {params}"
                    return await self.browser_tools.input_text(selector, text)
                elif "screenshot" in description:
                    return await self.browser_tools.take_screenshot(params.get("path", "screenshot.png"))
                else:
                    return f"Browser tool task not explicitly handled: {description}"

            elif tool_type == "os":
                if "click" in description:
                    x, y = params.get("x"), params.get("y")
                    if x is None or y is None:
                        return "Error: Missing 'x' or 'y' parameter for OS click task"
                    return self.os_tools.click_at(x, y)
                elif "type" in description:
                    text = params.get("text")
                    if text is None:
                        return "Error: Missing 'text' parameter for OS type task"
                    return self.os_tools.type_keys(text)
                elif "press" in description:
                    key = params.get("key")
                    if not key:
                        return "Error: Missing 'key' parameter for OS press task"
                    return self.os_tools.press_key(key)
                elif "screenshot" in description:
                    return self.os_tools.take_os_screenshot(params.get("path", "os_screenshot.png"))
                else:
                    return f"OS tool task not explicitly handled: {description}"

            else:
                return f"Unknown tool type: {tool_type}"
        except Exception as e:
            return f"Error executing task: {str(e)}"

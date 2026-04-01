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
        Executes a single task based on the tool type, action, and parameters.
        """
        tool_type = task.tool_type.lower()
        action = task.action
        params = task.parameters

        try:
            if tool_type == "browser":
                method = getattr(self.browser_tools, action, None)
                if method:
                    return await method(**params)
                else:
                    return f"Unknown browser action: {action}"
            elif tool_type == "os":
                method = getattr(self.os_tools, action, None)
                if method:
                    import inspect
                    if inspect.iscoroutinefunction(method):
                        return await method(**params)
                    else:
                        return method(**params)
                else:
                    return f"Unknown OS action: {action}"
            else:
                return f"Unknown tool type: {tool_type}"
        except Exception as e:
            return f"Error executing {tool_type} action '{action}': {str(e)}"

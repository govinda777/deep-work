import asyncio
import datetime
from src.agents.orchestrator import Orchestrator

class TaskScheduler:
    """
    Schedules goals for execution by the Orchestrator.
    """
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.active_tasks = []

    async def schedule_once(self, goal: str, delay_seconds: int):
        """
        Schedules a goal for one-time execution after a delay.
        """
        print(f"Scheduling goal '{goal}' in {delay_seconds} seconds...")

        async def delayed_execution():
            await asyncio.sleep(delay_seconds)
            print(f"Executing scheduled goal: {goal}")
            await self.orchestrator.run(goal)

        task = asyncio.create_task(delayed_execution())
        self.active_tasks.append(task)
        return task

    async def schedule_periodic(self, goal: str, interval_seconds: int, immediate=True):
        """
        Schedules a goal for periodic execution.
        """
        print(f"Scheduling periodic goal '{goal}' every {interval_seconds} seconds...")

        async def periodic_execution():
            if not immediate:
                await asyncio.sleep(interval_seconds)
            while True:
                print(f"Executing periodic goal: {goal}")
                try:
                    await self.orchestrator.run(goal)
                except Exception as e:
                    print(f"Periodic task error for '{goal}': {e}")
                await asyncio.sleep(interval_seconds)

        task = asyncio.create_task(periodic_execution())
        self.active_tasks.append(task)
        return task

    def stop_all(self):
        """
        Cancels all active scheduled tasks.
        """
        for task in self.active_tasks:
            task.cancel()
        self.active_tasks = []

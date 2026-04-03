import asyncio
import os
import sys
from dotenv import load_dotenv
from src.agents.orchestrator import Orchestrator
from src.memory.pinecone_manager import MemoryManager
from src.agents.scheduler import TaskScheduler

load_dotenv()

async def ainput(prompt: str) -> str:
    """Non-blocking input for asyncio."""
    return await asyncio.to_thread(input, prompt)

async def main():
    print("Initializing Deep-Work System...")

    # Initialize Memory
    try:
        memory = MemoryManager()
        print("Memory Manager Initialized.")
    except Exception as e:
        print(f"Error initializing memory: {e}")
        return

    # Initialize Orchestrator
    orchestrator = Orchestrator(memory=memory)
    print("Orchestrator Initialized.")

    # Initialize Scheduler
    scheduler = TaskScheduler(orchestrator=orchestrator)
    print("Scheduler Initialized.")

    while True:
        goal = await ainput("\nEnter your goal (or 'exit' to quit): ")
        if goal.lower() == 'exit':
            break

        if not goal:
            continue

        print("\nChoose execution mode:")
        print("1. Immediate")
        print("2. Schedule Once (Delayed)")
        print("3. Schedule Periodic")
        mode = await ainput("Select mode (1/2/3): ")

        if mode == '1':
            try:
                print(f"\nProcessing goal: {goal}")
                final_state = await orchestrator.run(goal)
                print("\nGoal completed!")
                print(f"Number of tasks executed: {len(final_state['results'])}")
            except Exception as e:
                print(f"An error occurred during execution: {e}")
        elif mode == '2':
            try:
                delay_str = await ainput("Enter delay in seconds: ")
                delay = int(delay_str)
                await scheduler.schedule_once(goal, delay)
                print(f"Goal scheduled to run in {delay} seconds.")
            except ValueError:
                print("Invalid delay value. Must be an integer.")
        elif mode == '3':
            try:
                interval_str = await ainput("Enter interval in seconds: ")
                interval = int(interval_str)
                await scheduler.schedule_periodic(goal, interval)
                print(f"Goal scheduled to run every {interval} seconds.")
            except ValueError:
                print("Invalid interval value. Must be an integer.")
        else:
            print("Invalid mode selected.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

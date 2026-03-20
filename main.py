import asyncio
import os
from dotenv import load_dotenv
from src.agents.orchestrator import Orchestrator
from src.memory.pinecone_manager import MemoryManager

load_dotenv()

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

    while True:
        goal = input("\nEnter your goal (or 'exit' to quit): ")
        if goal.lower() == 'exit':
            break

        if not goal:
            continue

        try:
            print(f"\nProcessing goal: {goal}")
            final_state = await orchestrator.run(goal)
            print("\nGoal completed!")
            print(f"Number of tasks executed: {len(final_state['results'])}")
        except Exception as e:
            print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())

# Deep-Work Technical Documentation

## 1. Architecture Overview
The Deep-Work system follows a **Planner-Actor-Validator** architecture orchestrated using **LangGraph**. This allows for a robust, self-correcting autonomous agent capable of both web and OS automation.

### 1.1 The Orchestrator (`src/agents/orchestrator.py`)
The Orchestrator manages the agent's state and lifecycle. It defines a graph with three primary nodes:
- **Plan**: Decomposes a goal into a sequence of tasks.
- **Execute**: Carries out a single task using the Actor.
- **Validate**: Checks if the task's expected outcome was achieved.

### 1.2 Memory Management with Pinecone (`src/memory/pinecone_manager.py`)
Deep-Work uses **Pinecone** as a vector database to manage episodic and semantic memory.
- **Episodic Memory**: Stores individual task executions, results, and plans.
- **Semantic Memory**: Allows the agent to retrieve relevant past experiences using OpenAI embeddings to inform current planning (RAG).
- **Async Support**: Implements `aadd_memory` and `asearch_memory` for efficient, non-blocking I/O.

## 2. Core Components

### 2.1 Planner (`src/agents/planner.py`)
Uses GPT-4o to generate a structured `Plan` (a list of `Task` objects). The planner is provided with a detailed schema of all available Browser and OS actions to ensure high-fidelity plan generation.

### 2.2 Actor (`src/agents/actor.py`)
The execution arm of the system. It dispatches tasks to either `BrowserTools` or `OSTools` based on the task's `tool_type`.

### 2.3 Validator (`src/agents/validator.py`)
A vision-capable component that uses GPT-4o to compare the current system state (page summary and/or screenshot) against the task's `expected_outcome`.

### 2.4 Workflow Synthesizer (`src/agents/recorder.py`)
Upon successful completion of a goal, this component extracts the sequence of tasks and stores it in Pinecone as a "Workflow". The Orchestrator checks for these workflows when starting new goals to reuse proven sequences.

### 2.5 Task Scheduler (`src/agents/scheduler.py`)
Enables autonomous background operations. It supports:
- **Delayed Execution**: Runs a goal once after a specified delay.
- **Periodic Execution**: Repeatedly runs a goal at a fixed interval.

## 3. Tooling and Integration

### 3.1 Browser Automation (`src/tools/browser_tools.py`)
Powered by **Playwright**.
- **Session Persistence**: Saves and loads `storage_state` (cookies, local storage) to `session_state.json`, allowing the agent to stay logged into websites.
- **Page Summarization**: Generates a text-based representation of interactive DOM elements for efficient LLM processing.

### 3.2 OS Automation (`src/tools/os_tools.py`)
Powered by **PyAutoGUI**.
- **Coordinate-based Interaction**: Supports clicks, double-clicks, and drags at specific (x, y) pixels.
- **Headless Compatibility**: Includes mocks for environments without a physical display, supporting CI/CD and Dockerized execution with Xvfb.

## 4. Setup and Deployment

### 4.1 Environment Variables
The following keys are required in a `.env` file:
- `OPENAI_API_KEY`: For LLM reasoning and embeddings.
- `PINECONE_API_KEY`: For vector memory storage.
- `PINECONE_INDEX_NAME`: The name of your Pinecone index (e.g., `deep-work-memory`).
- `DISPLAY`: Set to `:99` when running in Docker with Xvfb.

### 4.2 Dockerized Execution
Deep-Work is designed to run in a container to ensure an isolated environment.
```bash
docker-compose up --build
```
This starts an **Xvfb** virtual display on `:99`, providing a GUI environment for Playwright and PyAutoGUI.

### 4.3 Testing and Coverage
Deep-Work maintains a high standard of reliability with over 90% test coverage.
- **Run Tests**: `PYTHONPATH=. python3 -m unittest discover tests`
- **Check Coverage**:
  ```bash
  pip install coverage
  PYTHONPATH=. coverage run -m unittest discover tests
  coverage report
  ```

## 5. Technical Stack
- **Language**: Python 3.12
- **Orchestration**: LangGraph
- **Memory**: Pinecone (Vector DB)
- **LLMs**: GPT-4o (Reasoning, Vision, Planning)
- **Automation**: Playwright (Browser), PyAutoGUI (OS)
- **Environment**: Docker, Xvfb

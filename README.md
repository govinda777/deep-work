# Deep-Work Agent System

**Deep-Work** is an autonomous digital agent designed for seamless web and OS-level automation. Built with **LangGraph** and powered by **GPT-4o**, it acts as a "motor cortex" for AI, capable of learning, reproducing, and managing complex digital workflows in isolated environments.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose
- API Keys: OpenAI, Pinecone

### 2. Environment Setup
Create a `.env` file based on `.env.example`:
```bash
OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=deep-work-memory
```

### 3. Run with Docker (Recommended)
```bash
docker-compose up --build
```
This starts the agent in an isolated container with an **Xvfb** virtual display, supporting both Browser (Playwright) and OS (PyAutoGUI) automation.

### 4. Interactive Mode
If running locally:
```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```
Enter your goal (e.g., "Open example.com and take a screenshot") and watch the agent work.

## 📚 Documentation
For in-depth technical details, architecture overview, and advanced usage, see the **[Technical Documentation](DOCUMENTATION.md)**.

## 🛠 Features
- **Pinecone Memory**: Episodic and semantic memory for past experience retrieval (RAG).
- **Session Persistence**: Maintains browser login states (cookies, local storage).
- **Planner-Actor-Validator**: Robust 3-agent orchestration with self-correction.
- **Task Scheduler**: One-time or periodic background goal execution.
- **Isolated Sandbox**: Dockerized environment for secure execution.
- **High Reliability**: Over 90% test coverage.

## 🧪 Testing
Run the comprehensive test suite:
```bash
PYTHONPATH=. python3 -m unittest discover tests
```

---
*Deep-Work: Empowering AI to bridge the gap between thought and digital action.*

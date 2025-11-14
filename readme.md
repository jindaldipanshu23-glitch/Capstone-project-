# AI Agent Capstone — Personal Finance for Students

This repository is a 5-day AI intensive capstone scaffold. Project goal: build a domain-specific AI agent that answers student personal finance questions (budgeting, student loans, scholarships, basic investing) clearly and asks clarifying questions when needed.

Highlights:
- Local-first: LangChain + OpenAI + Chroma (run locally or in Colab)
- Retrieval-augmented generation (RAG) with conversational memory
- FastAPI demo server to run a web-based chat interface
- Optional Vertex AI Agent Engine helper for later deployment

Quick start (local):
1. Create and activate a virtual environment:
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .\.venv\Scripts\activate   # Windows PowerShell
2. Install dependencies:
   pip install -r requirements.txt
3. Create a .env file with OPENAI_API_KEY and optional AGENT_DOMAIN and LLM_MODEL
4. Run the FastAPI demo:
   uvicorn src.server.app:app --reload --port 8000
5. Or run the CLI agent:
   python -m src.agent.local_agent

License: Apache-2.0  
Author: jindaldipanshu23-glitch

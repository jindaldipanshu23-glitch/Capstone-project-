# Usage Notes & Tips

1. Domain
   - Project uses "Personal Finance for Students" as the working domain. You can change AGENT_DOMAIN env var.

2. Adding more docs
   - Put `.txt` files into `data/docs/`. Each file becomes a source.

3. Running
   - First run will build the Chroma vectorstore (.chromadb directory).

4. Tuning
   - Edit SYSTEM_PROMPT in src/agent/local_agent.py to tune style, clarifying behavior, refusal policy.

5. Deployment
   - For a simple demo UI, run the FastAPI server: uvicorn src.server.app:app --reload --port 8000

6. Safety
   - Add explicit disclaimers for financial/legal advice.

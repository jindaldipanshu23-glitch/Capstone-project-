from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import asyncio

# Ensure repo root is on path so we can import src.agent.local_agent
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.agent import local_agent

class ChatRequest(BaseModel):
    message: str

app = FastAPI(title="Capstone Agent — Personal Finance (Students)")

# Global agent chain (loaded on startup)
agent_chain = None

@app.on_event("startup")
async def startup_event():
    global agent_chain
    # Build or load vectorstore and create agent
    try:
        if not os.path.exists(local_agent.PERSIST_DIR) or not os.listdir(local_agent.PERSIST_DIR):
            docs = local_agent.load_text_files('data/docs')
            if not docs:
                print('No docs found in data/docs. Add files or use sample_faq.txt')
            else:
                local_agent.build_vectorstore(docs)
        vectordb = local_agent.load_vectorstore()
        agent_chain = local_agent.create_agent(vectordb)
        print('Agent ready')
    except Exception as e:
        print('Error initializing agent:', e)

@app.post('/chat')
async def chat(req: ChatRequest):
    global agent_chain
    if agent_chain is None:
        raise HTTPException(status_code=503, detail='Agent not ready')
    # Run the agent in a thread to avoid blocking
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, lambda: agent_chain({'question': req.message}))
    answer = resp.get('answer') or resp.get('result') or ''
    sources = [d.metadata.get('source') for d in resp.get('source_documents', [])][:5]
    return {'answer': answer, 'sources': sources}

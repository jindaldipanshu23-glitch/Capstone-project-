"""
Local LangChain-based domain agent (RAG + conversational memory).

Run: python -m src.agent.local_agent
Requires OPENAI_API_KEY in environment (.env supported).
"""

import os
import sys
import glob
from typing import List

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. The agent will error when calling embeddings/LLM.")

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

DATA_DIR = "data/docs"
PERSIST_DIR = ".chromadb"

# Domain-specific system prompt (concise + ask clarifying questions)
SYSTEM_PROMPT = """You are a helpful, concise assistant specialized in Personal Finance for students.
- Give clear, actionable, and simple explanations suitable for students.
- When the user's question lacks necessary details, ask one short clarifying question.
- If you use facts from source documents, cite the document filename in brackets, e.g., [sample_faq.txt].
- If the question is outside the domain, say you cannot provide professional advice and offer general resources.
"""

def load_text_files(path: str) -> List[Document]:
    docs = []
    for file in glob.glob(os.path.join(path, "*")):
        if file.endswith(".txt"):
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
            docs.append(Document(page_content=text, metadata={"source": os.path.basename(file)}))
    return docs

def build_vectorstore(docs: List[Document], persist_directory: str = PERSIST_DIR):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    split_docs = []
    for d in docs:
        chunks = splitter.split_text(d.page_content)
        for i, c in enumerate(chunks):
            split_docs.append(Document(page_content=c, metadata={"source": d.metadata.get("source"), "chunk": i}))
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory=persist_directory)
    vectordb.persist()
    return vectordb

def load_vectorstore(persist_directory: str = PERSIST_DIR):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectordb

def create_agent(vectordb, domain_name: str = "Personal Finance (Students)", temperature: float = 0.2):
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    chat = ChatOpenAI(temperature=temperature, model=model_name, openai_api_key=OPENAI_API_KEY)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    system_msg = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
    human_msg = HumanMessagePromptTemplate.from_template("{input}")
    prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return chain

def interactive_loop(chain):
    print("Agent started. Type 'exit' to quit.")
    while True:
        q = input("\nUser: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        resp = chain({"question": q})
        answer = resp.get("answer") or resp.get("result") or ""
        print("\nAssistant:\n", answer.strip())
        sources = resp.get("source_documents", [])
        if isinstance(sources, list) and sources:
            print("\nSources:")
            for s in sources[:3]:
                print("-", s.metadata.get("source"))

def main():
    domain_name = os.getenv("AGENT_DOMAIN", "Personal Finance — Students")
    if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
        print("Building vectorstore from documents in", DATA_DIR)
        docs = load_text_files(DATA_DIR)
        if not docs:
            print("No documents found in", DATA_DIR, ". Please add docs or use sample.")
            sys.exit(1)
        vectordb = build_vectorstore(docs)
    else:
        vectordb = load_vectorstore()
    agent = create_agent(vectordb, domain_name=domain_name)
    interactive_loop(agent)

if __name__ == "__main__":
    main()

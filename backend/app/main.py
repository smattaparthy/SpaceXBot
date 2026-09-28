from fastapi import FastAPI
from pydantic import BaseModel

from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.openai_chat_service import generate_answer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mission Control RAG API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "Mission Control RAG API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    
    chunks = retrieve_relevant_chunks(
        question=request.question,
        top_k=3,
    )

    
    answer = generate_answer(
        question=request.question,
        chunks=chunks,
    )

    
    return {
        "question": request.question,
        "answer": answer,
        "sources": [
            {
                "file_name": chunk["file_name"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
            }
            for chunk in chunks
        ],
    }
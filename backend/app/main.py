import logging
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAIError
from pinecone.errors import PineconeError
from pydantic import BaseModel, StringConstraints

from app.config import RETRIEVAL_TOP_K
from app.services.openai_chat_service import generate_answer
from app.services.retrieval_service import retrieve_relevant_chunks


logger = logging.getLogger(__name__)

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
    question: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=1000),
    ]


class Source(BaseModel):
    file_name: str
    chunk_id: int
    score: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]


@app.get("/")
def root():
    return {
        "message": "Mission Control RAG API is running"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        chunks = retrieve_relevant_chunks(
            question=request.question,
            top_k=RETRIEVAL_TOP_K,
        )
    except (OpenAIError, PineconeError):
        logger.exception("Retrieval failed")
        raise HTTPException(
            status_code=502,
            detail="Could not search the knowledge base. Please try again.",
        )

    try:
        answer = generate_answer(
            question=request.question,
            chunks=chunks,
        )
    except OpenAIError:
        logger.exception("Answer generation failed")
        raise HTTPException(
            status_code=502,
            detail="Could not generate an answer. Please try again.",
        )

    return ChatResponse(
        question=request.question,
        answer=answer,
        sources=[
            Source(
                file_name=chunk["file_name"],
                chunk_id=chunk["chunk_id"],
                score=chunk["score"],
            )
            for chunk in chunks
        ],
    )

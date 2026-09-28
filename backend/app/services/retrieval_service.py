import os

from pinecone import Pinecone

from app.services.embedding_service import create_embedding


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "spacex-rag",
)

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    PINECONE_INDEX_NAME
)


def retrieve_relevant_chunks(
    question,
    top_k=3,
):
    
    query_embedding = create_embedding(question)


    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    
    chunks = []

    for match in results["matches"]:
        chunks.append(
            {
                "score": match["score"],
                "text": match["metadata"]["text"],
                "file_name": match["metadata"]["file_name"],
                "chunk_id": match["metadata"]["chunk_id"],
            }
        )

    return chunks
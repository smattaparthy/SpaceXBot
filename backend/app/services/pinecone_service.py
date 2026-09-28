import os
from pinecone import Pinecone


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


def upsert_chunk(
    vector_id,
    embedding,
    text,
    file_name,
    chunk_id,
    category=None,
    vehicle=None,
):
    metadata = {
        "text": text,
        "file_name": file_name,
        "chunk_id": chunk_id,
    }

    if category:
        metadata["category"] = category

    if vehicle:
        metadata["vehicle"] = vehicle

    index.upsert(
        vectors=[
            {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata,
            }
        ]
    )
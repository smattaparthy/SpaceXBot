from app.clients import get_pinecone_index


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

    get_pinecone_index().upsert(
        vectors=[
            {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata,
            }
        ]
    )

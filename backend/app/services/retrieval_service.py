from app.clients import get_pinecone_index
from app.services.embedding_service import create_embedding


def retrieve_relevant_chunks(
    question,
    top_k=3,
):
    query_embedding = create_embedding(question)

    results = get_pinecone_index().query(
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

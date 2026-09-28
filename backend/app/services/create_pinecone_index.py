import os

from pinecone import Pinecone, ServerlessSpec


pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

pc.create_index(
    name="spacex-rag",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1",
    ),
)

print("Pinecone index created.")
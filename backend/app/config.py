import os


OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.4-mini")

# Changing the embedding model means re-running ingestion (vectors must match).
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "spacex-rag")

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "3"))

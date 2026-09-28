from app.clients import get_openai_client
from app.config import OPENAI_EMBEDDING_MODEL


def create_embedding(text):
    response = get_openai_client().embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding

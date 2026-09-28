from functools import cache

from openai import OpenAI
from pinecone import Pinecone

from app.config import PINECONE_INDEX_NAME


# Created on first use so the API (and tests) can start without keys.
# Both SDKs read OPENAI_API_KEY / PINECONE_API_KEY from the environment.

@cache
def get_openai_client() -> OpenAI:
    return OpenAI()


@cache
def get_pinecone_index():
    return Pinecone().Index(PINECONE_INDEX_NAME)

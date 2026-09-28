from app.clients import get_openai_client
from app.config import OPENAI_CHAT_MODEL


def generate_answer(question, chunks):
    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
    )

    prompt = f"""
You are a SpaceX knowledge assistant.

Answer the question only using the context below.

If the answer is not present in the context,
say that the information is not available
in the current knowledge base.

Context:
{context}

Question:
{question}
"""

    response = get_openai_client().responses.create(
        model=OPENAI_CHAT_MODEL,
        input=prompt,
    )

    return response.output_text

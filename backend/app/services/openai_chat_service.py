import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


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

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt,
    )

    return response.output_text
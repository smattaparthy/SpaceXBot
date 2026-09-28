from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)

from app.services.openai_chat_service import (
    generate_answer,
)


question = "What is Dragon?"

chunks = retrieve_relevant_chunks(
    question,
    top_k=3,
)

answer = generate_answer(
    question,
    chunks,
)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)
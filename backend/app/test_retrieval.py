from services.retrieval_service import retrieve_relevant_chunks


question = "What is Dragon?"

results = retrieve_relevant_chunks(
    question,
    top_k=3,
)

for result in results:
    print("\nScore:", result["score"])
    print("File:", result["file_name"])
    print("Chunk:", result["chunk_id"])
    print("Text:", result["text"])
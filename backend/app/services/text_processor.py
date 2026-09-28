def clean_text(text):
    cleaned = " ".join(text.split())
    return cleaned


def chunk_text(text, chunk_size=500):
    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks
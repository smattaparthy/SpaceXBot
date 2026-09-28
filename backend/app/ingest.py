"""Load documents from Azure Blob Storage into Pinecone.

Run from backend/:
    python -m app.ingest --dry-run   # show what would be uploaded
    python -m app.ingest             # embed and upsert

Vector IDs are `{file_name}-chunk-{n}`, so re-running overwrites existing
vectors instead of duplicating them.
"""

import argparse

from app.services.blob_service import download_document, list_documents
from app.services.document_extractor import extract_text, is_supported, parse_header
from app.services.text_processor import chunk_text, clean_text


def ingest(dry_run: bool) -> None:
    if not dry_run:
        # Imported here so a dry run never touches OpenAI or Pinecone.
        from app.services.embedding_service import create_embedding
        from app.services.pinecone_service import upsert_chunk

    total = 0

    for file_name in list_documents():
        if not is_supported(file_name):
            print(f"skip   {file_name} (unsupported type)")
            continue

        text = extract_text(file_name, download_document(file_name))
        header = parse_header(text)
        chunks = chunk_text(clean_text(text))

        for chunk_id, chunk in enumerate(chunks):
            vector_id = f"{file_name}-chunk-{chunk_id}"

            if not dry_run:
                upsert_chunk(
                    vector_id=vector_id,
                    embedding=create_embedding(chunk),
                    text=chunk,
                    file_name=file_name,
                    chunk_id=chunk_id,
                    category=header.get("category"),
                    vehicle=header.get("vehicle"),
                )

            total += 1

        print(
            f"{'plan' if dry_run else 'upsert'} {file_name}: {len(chunks)} chunk(s), "
            f"category={header.get('category')}, vehicle={header.get('vehicle')}"
        )

    print(f"{'Would upsert' if dry_run else 'Upserted'} {total} vector(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    ingest(parser.parse_args().dry_run)

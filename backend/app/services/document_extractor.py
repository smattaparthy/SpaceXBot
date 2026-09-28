from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def is_supported(file_name: str) -> bool:
    return Path(file_name).suffix.lower() in SUPPORTED_EXTENSIONS


def extract_text(file_name: str, data: bytes) -> str:
    if not is_supported(file_name):
        raise ValueError(f"Unsupported file type: {file_name}")

    return data.decode("utf-8-sig")


def parse_header(text: str) -> dict[str, str]:
    """Read the leading `key: value` block that ends at the first blank line."""
    header = {}

    for line in text.splitlines():
        if not line.strip():
            break

        key, sep, value = line.partition(":")
        if not sep:
            break

        header[key.strip()] = value.strip()

    return header

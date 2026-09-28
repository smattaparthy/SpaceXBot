from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env before any service module reads os.getenv at import time.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# SpaceXBot — Build Plan

## What this project is

A SpaceX knowledge chatbot ("Mission Control"). It uses RAG (retrieval-augmented generation):
SpaceX documents are split into chunks and stored in a vector database. When a user asks a
question, the backend finds the most relevant chunks and has OpenAI write an answer using only
those chunks.

```
Browser (Next.js, :3000)                FastAPI backend (:8000)
  ChatWidget  ── POST /chat ──────────►  main.py
                                          ├─ embedding_service   → OpenAI embeddings (text-embedding-3-small)
                                          ├─ retrieval_service   → Pinecone index (top 3 chunks)
                                          └─ openai_chat_service → OpenAI Responses API
                                         returns { answer, sources[] }

Ingestion (partly built):
  Azure Blob "spacexdocuments/spacex" → extract text (MISSING) → chunk → embed → upsert to Pinecone
```

## What you need to run it

| Item | Where it goes |
|---|---|
| OpenAI API key | `backend/.env` → `OPENAI_API_KEY` |
| Chat model (optional) | `backend/.env` → `OPENAI_CHAT_MODEL` (default `gpt-5.4-mini`; `gpt-5.4-nano` also allowed). Embeddings use `text-embedding-3-small`; changing that means re-ingesting |
| Pinecone API key + index name | `backend/.env` → `PINECONE_API_KEY`, `PINECONE_INDEX_NAME` (`spacex-rag`) |
| Azure Blob access (ingestion only) | `az login` + "Storage Blob Data Reader" role on `spacexdocuments` |

**Azure login:** `blob_service.py` deliberately ignores `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` /
`AZURE_TENANT_ID` environment variables (`exclude_environment_credential=True`). Those are often
exported globally, for example in `~/.zshrc` for other tools, and would override `az login`.
Locally it uses `az login`; on Azure it uses managed identity. Don't put Azure secrets in `backend/.env`.
| Node 20+ | frontend |
| Python 3.10+ | backend |

Setup:

```bash
# Keys
cp backend/.env.example backend/.env   # then fill in values

# Frontend → http://localhost:3000
npm install
npm run dev

# Backend → http://127.0.0.1:8000 (run from backend/)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

`backend/app/__init__.py` loads `backend/.env` automatically before any service reads its keys.

Load or refresh documents (from `backend/`):

```bash
python -m app.ingest --dry-run   # list what would be uploaded; writes nothing
python -m app.ingest             # embed + upsert into Pinecone
python -m pytest tests           # unit tests
```

## Current state (2026-09-28)

- **Works end to end** (backend verified in-process): retrieval + `gpt-5.4-mini` answer correctly,
  and off-topic questions return "not available in the current knowledge base".
- Pinecone `spacex-rag` holds 5 vectors (`{file_name}-chunk-0`, one per document), loaded by
  `python -m app.ingest`, with `category`/`vehicle` metadata.
- Pinecone `spacex-rag1` is an unused, empty index left over from the old default name. It can be deleted.

## Known issues

1. Chunking uses fixed 500-word blocks with no overlap (fine for the current ~100-word docs).
2. CORS only allows `localhost:3000`, so the deployed frontend URL must be added (Phase 5).
3. The knowledge base is 5 short synthetic demo documents, so answers are basic.

Fixed: committed `.venv`/`__pycache__`, missing ingestion, the `spacex-rag1` default, the
`test_retrieval.py` import, the hardcoded, unavailable `gpt-5.6` model, raw 500s from the API, and
the app needing keys just to start, the hardcoded API URL, the chat widget with no error
handling or sources, and the frontend leftovers.

## Plan of action

### Phase 1: make it runnable
- [x] `backend/.env.example` template for keys
- [x] `backend/requirements.txt`
- [x] Auto-load `backend/.env` (`backend/app/__init__.py`)
- [x] Remove `backend/.venv` and `__pycache__` from git and add them to `.gitignore`
- [x] Fix the `spacex-rag1` default so every module uses `spacex-rag`
- [x] Fix the `test_retrieval.py` import
- [x] Chat model as a setting (`OPENAI_CHAT_MODEL`, default `gpt-5.4-mini`)
- [x] Update `.env.example`: comment out the Azure lines, add `OPENAI_CHAT_MODEL`
- [x] Frontend: API address from `NEXT_PUBLIC_API_URL` (defaults to `http://127.0.0.1:8000`; set it
      in `.env.local` or at build time, since Next.js bakes it in during `next build`)
- [x] Rewrite the README with setup steps

### Phase 2: ingestion pipeline (key missing piece)

Current documents in Azure (`spacexdocuments` / container `spacex`), checked 2026-09-28:

| File | Category | Vehicle |
|---|---|---|
| `company_overview.txt` | company | — |
| `dragon_overview.txt` | vehicle | Dragon |
| `falcon9_overview.txt` | vehicle | Falcon 9 |
| `launch_operations.txt` | operations | — |
| `starship_overview.txt` | vehicle | Starship |
| `spacex_rag_demo_docs.zip` | original upload; skip it (or delete it) | |

Each file is plain text, about 100 words, with a `key: value` header block (`document_id`, `title`,
`category`, `vehicle`, ...) followed by a blank line and the body. These are synthetic demo documents.

- [x] Implement `document_extractor.py`: decode `.txt`/`.md` and parse the header block
      (PDF support via `pypdf` can wait until PDFs are uploaded)
- [x] Pass header `category` and `vehicle` through to `pinecone_service.upsert_chunk`
- [x] Title stays in the chunk text (the whole header is embedded with the body)
- [x] `backend/app/ingest.py` with `--dry-run`: list blobs → skip non-text (.zip) → extract → clean → chunk → embed → upsert
- [x] Stable vector IDs `{file_name}-chunk-{n}`, matching the existing vectors, so re-runs overwrite them
- [x] Dry run verified: 5 docs, zip skipped, generated text identical to the stored vectors
- [x] Try it out: "What is Dragon?" and "How does Falcon 9 reuse its first stage?" answer
      correctly; "Who won the 2022 World Cup?" returns "not available"
- [x] Run `python -m app.ingest` for real: 5 vectors, now with `category`/`vehicle` metadata
- [ ] Optional: overlapping chunks (only matters once bigger docs are uploaded)
- [ ] Optional: local-folder source so ingestion can be tested without Azure

### Phase 3: make the backend reliable
- [x] Central config module `app/config.py` (chat and embedding model, index name, `RETRIEVAL_TOP_K`)
- [x] `app/clients.py` creates OpenAI/Pinecone clients on first use, so the app and tests start without keys
- [x] Reject blank questions or ones over 1,000 characters (422); OpenAI or Pinecone failures return 502
      with a readable message and are logged server-side
- [x] Typed `/chat` response (`question`, `answer`, `sources[]`)
- [x] Replaced the print scripts with pytest: 15 tests (API with faked services + document extractor),
      run with no keys set

### Phase 4: chat interface
- [x] Convert components to TypeScript (`ChatWidget.tsx`, `NavBar.tsx`); removed the unused CSS module
- [x] Restore Tailwind v4 with a small theme: true black, white, and the logo's silver; Barlow type
- [x] Conversation laid out as a log: each question is a heading, the answer below; "New chat" resets
- [x] Loading ("Searching the knowledge base…"), error message with "Try again", empty-input guard,
      Enter to send and Shift+Enter for a new line, 1,000-character limit
- [x] Sources listed under each answer. Loosely related matches are hidden (score < 0.4 or more
      than 0.15 below the best match), so off-topic answers show none
- [x] Real page title and description
- [x] Checked in the browser at desktop and phone widths: suggestion click, typed question,
      off-topic question, backend down
- [ ] Optional: stream answers as they're written

### Phase 5: deployment (optional)
- [ ] Dockerfile for the backend
- [ ] Deploy the backend (Azure Container Apps) and the frontend (Vercel or Azure Static Web Apps)
- [ ] Lock CORS to the deployed frontend URL

## Done when

A user opens the site, asks "What is Dragon?", and gets an answer based on the ingested
SpaceX documents, with the source file names shown underneath.

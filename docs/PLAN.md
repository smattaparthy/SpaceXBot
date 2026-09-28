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
| Pinecone API key + index name | `backend/.env` → `PINECONE_API_KEY`, `PINECONE_INDEX_NAME` |
| Azure Blob access (ingestion only) | `az login`, or service principal values in `backend/.env` |
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

## Known issues

1. `backend/.venv` (1,342 files, built on Linux, empty) and `__pycache__/*.pyc` are committed to git.
2. Ingestion is missing: `document_extractor.py` is empty and nothing runs blob → extract → chunk → embed → upsert.
3. Index name mismatch: `pinecone_service.py` defaults to `spacex-rag1`, while retrieval and the
   create script use `spacex-rag`. Setting `PINECONE_INDEX_NAME` in `.env` works around it.
4. `ChatWidget.jsx` hardcodes `http://127.0.0.1:8000/chat`.
5. The chat widget has no error handling (it stays on "Thinking..." forever), accepts empty
   questions, and never shows the `sources` the API returns.
6. The API has no error handling: a failure at OpenAI or Pinecone comes back as a raw 500.
7. `test_retrieval.py` imports `services.` instead of `app.services.`.
8. The chat model name `gpt-5.6` is hardcoded. It should be a setting.
9. Frontend leftovers: `NavBar.module.css` is unused, the Tailwind import was removed so the
   classes in `layout.tsx` do nothing, the page title is "Create Next App", and the README is the starter template.
10. Chunking uses fixed 500-word blocks with no overlap.

## Plan of action

### Phase 1: make it runnable
- [x] `backend/.env.example` template for keys
- [x] `backend/requirements.txt`
- [x] Auto-load `backend/.env` (`backend/app/__init__.py`)
- [ ] Remove `backend/.venv` and `__pycache__` from git and add them to `.gitignore`
- [ ] Make the index name a single setting (fix the `spacex-rag1` default)
- [ ] Fix the `test_retrieval.py` import
- [ ] Frontend: move the API address into `NEXT_PUBLIC_API_URL` (`.env.local`)
- [ ] Rewrite the README with setup steps

### Phase 2: ingestion pipeline (key missing piece)
- [ ] Implement `document_extractor.py` (PDF via `pypdf`, plus `.txt` and `.md`)
- [ ] Improve chunking: overlapping chunks
- [ ] `backend/app/ingest.py`: blob → extract → clean → chunk → embed → upsert
- [ ] Stable vector IDs (`{file_name}-{chunk_id}`) so re-runs update chunks instead of duplicating them
- [ ] Local-folder option so ingestion can be tested without Azure
- [ ] Run ingestion once and confirm the index has data

### Phase 3: make the backend reliable
- [ ] Central config module (keys, index name, chat model, top_k)
- [ ] Reject empty questions; return clear errors when OpenAI or Pinecone fails
- [ ] Replace the print scripts with pytest tests that fake the OpenAI and Pinecone calls (in `backend/tests/`)

### Phase 4: chat interface
- [ ] Convert components to TypeScript
- [ ] Restore Tailwind; build a SpaceX-styled layout
- [ ] Message history, loading and error states, empty-input guard
- [ ] Show sources under each answer
- [ ] Optional: stream answers as they're written
- [ ] Real page title and metadata

### Phase 5: deployment (optional)
- [ ] Dockerfile for the backend
- [ ] Deploy the backend (Azure Container Apps) and the frontend (Vercel or Azure Static Web Apps)
- [ ] Lock CORS to the deployed frontend URL

## Done when

A user opens the site, asks "What is Dragon?", and gets an answer based on the ingested
SpaceX documents, with the source file names shown underneath.

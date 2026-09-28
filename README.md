# SpaceXBot (Mission Control)

A SpaceX knowledge chatbot. Questions are answered only from documents in the knowledge base
(retrieval-augmented generation): the backend finds the most relevant document chunks in Pinecone
and has OpenAI write an answer from them, listing the documents it used.

- **Frontend:** Next.js 16 + React 19 + Tailwind v4 (`app/`)
- **Backend:** FastAPI (`backend/app/`)
- **Services:** OpenAI (embeddings + answers), Pinecone (vector search), Azure Blob Storage (source documents)

The build plan, current state, and known issues are in [docs/PLAN.md](docs/PLAN.md).

## Setup

You need Node 20.9+, Python 3.10+, an OpenAI API key, and a Pinecone API key. Loading documents
also needs `az login` with the "Storage Blob Data Reader" role on the `spacexdocuments` storage account.

```bash
# 1. Keys
cp backend/.env.example backend/.env    # fill in OPENAI_API_KEY and PINECONE_API_KEY

# 2. Backend → http://127.0.0.1:8000
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Frontend → http://localhost:3000 (second terminal, repo root)
npm install
npm run dev
```

The frontend calls `http://127.0.0.1:8000` by default. To point it somewhere else, set
`NEXT_PUBLIC_API_URL` in `.env.local` (it is baked in when `next build` runs).

## Loading documents

Documents live in the `spacex` container of the `spacexdocuments` Azure storage account.
From `backend/`:

```bash
python -m app.ingest --dry-run   # show what would be uploaded; writes nothing
python -m app.ingest             # embed and upsert into Pinecone (safe to re-run)
```

## Checks

```bash
cd backend && python -m pytest tests   # backend tests (no keys needed)
npx tsc --noEmit && npm run lint       # frontend type-check and lint
npm run build                          # frontend production build
```

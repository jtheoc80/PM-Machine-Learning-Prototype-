````markdown name=README.md
```markdown
# Supabase + pgvector RAG starter for Emerson J-series valve maintenance (OpenAI embeddings)

This prototype ingests maintenance manual text (e.g., Emerson J-series excerpts) into Supabase (Postgres + pgvector), stores chunk embeddings using OpenAI embeddings (text-embedding-3-small), and runs a Retrieval-Augmented Generation (RAG) workflow using OpenAI for generation.

Files added:
- scripts/create_supabase_table.sql — SQL to create the documents table + RPC function `match_documents`. Uses vector(1536) for OpenAI embeddings.
- scripts/ingest_emerson_j_series.py — Chunk text and upsert OpenAI embeddings into Supabase.
- scripts/query_supabase_rag.py — Embed user query with OpenAI, retrieve top-K chunks using `match_documents`, assemble prompt, and call OpenAI ChatCompletion to generate recommendations.

Setup
1. Enable pgvector extension in Supabase (many Supabase projects include it).
2. Run the SQL file in the Supabase SQL editor:
   - Copy scripts/create_supabase_table.sql into the SQL editor and execute.
3. Install Python deps:
   - python -m pip install supabase openai numpy
4. Export env vars:
   - export SUPABASE_URL="https://xyz.supabase.co"
   - export SUPABASE_KEY="service_role_or_anon_key"  # Use service_role if you need to write from server code
   - export OPENAI_API_KEY="sk-..."

Ingesting a manual excerpt
- Place a plaintext excerpt of the Emerson J-series maintenance instructions in data/emerson_j_series.txt.
- Run:
  python scripts/ingest_emerson_j_series.py --input-file data/emerson_j_series.txt --source-id emerson_j_series_v1 --valve-model "J-series"

Querying
- Example:
  python scripts/query_supabase_rag.py --query "seat leakage after setpoint reached" --top-k 5 --valve-model "J-series"

Security & operational notes
- Use the service_role key for server-side ingestion and ensure Row Level Security (RLS) rules for any client keys.
- Confirm licensing: proceed only with internal, non-public storage of authorized Emerson materials.
- For production: consider batching, rate limits, monitoring, and a human-in-the-loop approval step for safety-critical recommendations.
```
````
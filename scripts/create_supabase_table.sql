-- SQL to run in your Supabase SQL editor once.
-- Creates documents table with a 1536-dim embedding vector (matches OpenAI text-embedding-3-small).
-- Also creates an RPC function `match_documents` to perform nearest-neighbor search.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type text,         -- 'manual'|'repair_log' etc.
  source_id text,           -- e.g., file name or repair ID
  valve_model text,
  timestamp timestamptz,
  text_content text,
  metadata jsonb,
  embedding vector(1536)     -- 1536 dims for text-embedding-3-small
);

-- Index for faster ANN (ivfflat recommended for larger datasets)
-- NOTE: after creating ivfflat index, run `ANALYZE documents;` and tune `lists` for your dataset.
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- RPC function to search by a float8[] vector parameter (Supabase can call RPC)
-- Accepts the query as a float8[] array; the function casts it to vector for distance computations.
CREATE OR REPLACE FUNCTION match_documents(query float8[], k int, p_valve_model text DEFAULT NULL)
RETURNS TABLE (
  id uuid,
  source_type text,
  source_id text,
  valve_model text,
  text_content text,
  metadata jsonb,
  distance double precision
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    id,
    source_type,
    source_id,
    valve_model,
    text_content,
    metadata,
    embedding <-> query::vector AS distance
  FROM documents
  WHERE (p_valve_model IS NULL OR valve_model = p_valve_model)
  ORDER BY embedding <-> query::vector
  LIMIT k;
END;
$$ LANGUAGE plpgsql STABLE;
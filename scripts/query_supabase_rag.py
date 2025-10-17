#!/usr/bin/env python3
"""
Query pipeline for Supabase + pgvector using OpenAI embeddings.

Usage:
  export SUPABASE_URL=...
  export SUPABASE_KEY=...
  export OPENAI_API_KEY=...
  python scripts/query_supabase_rag.py --query "valve leaking at seat after setpoint reached" --top-k 5

This script:
- embeds the user query using OpenAI embeddings (text-embedding-3-small),
- calls the Postgres RPC function `match_documents` to retrieve nearest chunks,
- assembles a prompt that asks the OpenAI LLM to produce short recommendations with citations.
"""
import os
import argparse
import numpy as np
from supabase import create_client

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_CHAT_MODEL = "gpt-4o-mini"

def get_query_embedding_openai(query: str):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
    resp = openai.Embedding.create(input=[query], model=OPENAI_EMBEDDING_MODEL)
    return np.array(resp["data"][0]["embedding"], dtype=float)

def query_supabase_vectors(supabase, query_embedding, top_k=5, valve_model=None):
    # Call RPC match_documents with float8[]
    payload = {"query": list(map(float, query_embedding)), "k": top_k, "p_valve_model": valve_model}
    res = supabase.rpc("match_documents", payload).execute()
    if res.error:
        raise RuntimeError(f"Supabase RPC error: {res.error}")
    return res.data

def build_prompt(query: str, contexts):
    context_text = "\n\n---\n\n".join([f"[{i+1}] {c['text_content']}" for i, c in enumerate(contexts)])
    prompt = f"""You are a valve maintenance assistant. Use ONLY the following context to make recommendations.

Context:
{context_text}

Customer issue:
{query}

Return:
1) A short (1-2 sentence) recommendation.
2) Clear actionable steps (numbered).
3) For each step, cite which context chunk(s) support it by number in square brackets.
4) If you are uncertain, say so and advise inspection steps.
"""
    return prompt

def call_openai_chat(prompt: str, model: str = OPENAI_CHAT_MODEL, temperature: float = 0.0):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY required to call OpenAI")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"system", "content":"You are a technical valve assistant. Use only the context provided."},
                  {"role":"user", "content":prompt}],
        max_tokens=600,
        temperature=temperature,
    )
    return resp["choices"][0]["message"]["content"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--valve-model", default="J-series")
    args = parser.parse_args()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    q_emb = get_query_embedding_openai(args.query)

    contexts = query_supabase_vectors(supabase, q_emb, top_k=args.top_k, valve_model=args.valve_model)
    if not contexts:
        print("No contexts found for the query.")
        return

    prompt = build_prompt(args.query, contexts)
    answer = call_openai_chat(prompt)
    print("Recommendation:\n")
    print(answer)

if __name__ == "__main__":
    main()
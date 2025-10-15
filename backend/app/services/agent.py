from __future__ import annotations
from typing import List, Dict, Any
from backend.app.core.config import get_settings
from backend.app.services.vectorstore import get_vector_store
from backend.app.services.embeddings import embed_texts
from backend.app.services.llm import generate_response

_settings = get_settings()


def _make_system_prompt() -> str:
    return (
        "You are a specialist engineer for industrial pressure relief valves (PRV). "
        "You analyze requirements (process fluid, set pressure, temperature, flow rate, code/standard like ASME/API), materials, and certifications. "
        "Use only provided context documents and your domain knowledge to recommend options, trade-offs, sizing approaches, and standards compliance. "
        "Return clear, actionable guidance with assumptions, and cite sources by their source URI when relevant."
    )


def _build_rag_prompt(query: str, contexts: List[str], metadatas: List[Dict[str, Any]]) -> str:
    sources_list = []
    for md in metadatas:
        src = md.get("source") if isinstance(md, dict) else None
        if src and src not in sources_list:
            sources_list.append(src)
    context_text = "\n\n".join(contexts)
    sources_text = "\n".join(f"- {s}" for s in sources_list)
    instructions = (
        "Answer the user question using only the CONTEXT. "
        "If the answer is not in the context, say you do not have sufficient information. "
        "Include a short bullet list of recommended next steps."
    )
    return f"CONTEXT:\n{context_text}\n\nSOURCES:\n{sources_text}\n\nQUESTION:\n{query}\n\n{instructions}"


def answer_query(query: str, top_k: int | None = None) -> Dict[str, Any]:
    vs = get_vector_store()
    k = top_k or _settings.top_k
    # Embed query to align with precomputed embeddings for better accuracy
    q_emb = embed_texts([query])
    results = vs.query(query_embeddings=q_emb, n_results=k)
    documents: List[str] = results.get("documents", [[]])[0]
    metadatas: List[Dict[str, Any]] = results.get("metadatas", [[]])[0]
    ids: List[str] = results.get("ids", [[]])[0]
    distances: List[float] = results.get("distances", [[]])[0]

    prompt = _build_rag_prompt(query, documents, metadatas)
    system_prompt = _make_system_prompt()
    answer = generate_response(prompt, system=system_prompt)

    # Build sources
    sources = []
    for i in range(len(documents)):
        snippet = documents[i][:400]
        src = metadatas[i].get("source") if i < len(metadatas) else None
        score = 1.0 - distances[i] if i < len(distances) else None
        sources.append({
            "id": ids[i] if i < len(ids) else f"doc-{i}",
            "uri": src,
            "score": score,
            "snippet": snippet,
        })

    return {"answer": answer, "sources": sources}
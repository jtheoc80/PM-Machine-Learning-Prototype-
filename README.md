PRV Specialist Agent (RAG)

Quick start

1) Set environment

- OPENAI_API_KEY=... (if using OpenAI for LLM/embeddings)
- LLM_PROVIDER=openai|ollama
- OLLAMA_MODEL=llama3.1 (if using ollama)

2) Run backend

- pip install -r requirements.txt
- uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

3) Run UI

- streamlit run ui/app.py

Endpoints

- POST /api/upload: multipart files
- POST /api/crawl: {seeds:["https://example.com"], allowed_domains:["example.com"], max_pages:100}
- POST /api/chat: {query:"...", top_k:8}

import os
import json
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")

st.set_page_config(page_title="PRV Specialist Agent", layout="wide")

st.title("Pressure Relief Valve Specialist Agent")

with st.sidebar:
    st.header("Data Ingestion")
    # File upload
    uploaded = st.file_uploader("Upload documents (CSV/XLSX/PDF/TXT)", type=["csv","xlsx","xls","pdf","txt","md"], accept_multiple_files=True)
    if st.button("Ingest Uploaded Files") and uploaded:
        files = [("files", (f.name, f.getvalue())) for f in uploaded]
        resp = requests.post(f"{API_BASE}/upload", files=files)
        if resp.ok:
            st.success(resp.json().get("message"))
        else:
            st.error("Upload failed")

    st.header("Web Crawl")
    seeds = st.text_area("Seed URLs (one per line)").strip().splitlines()
    allowed = st.text_input("Allowed domains (comma-separated, optional)")
    max_pages = st.number_input("Max pages", min_value=10, max_value=2000, value=100, step=10)
    if st.button("Start Crawl") and seeds:
        body = {
            "seeds": seeds,
            "allowed_domains": [d.strip() for d in allowed.split(",") if d.strip()] or None,
            "max_pages": int(max_pages),
        }
        resp = requests.post(f"{API_BASE}/crawl", json=body)
        if resp.ok:
            st.success(resp.json().get("message"))
        else:
            st.error("Crawl failed")

st.header("Ask the Specialist")
query = st.text_input("Your question about PRVs")
top_k = st.slider("Retriever top_k", min_value=3, max_value=20, value=8)
if st.button("Ask") and query:
    body = {"query": query, "top_k": int(top_k)}
    with st.spinner("Thinking..."):
        resp = requests.post(f"{API_BASE}/chat", json=body)
    if resp.ok:
        data = resp.json()
        st.subheader("Answer")
        st.write(data.get("answer"))
        st.subheader("Sources")
        for s in data.get("sources", []):
            uri = s.get('uri') or 'local file'
            score = s.get('score')
            score_text = f"{score:.3f}" if isinstance(score, (float, int)) else 'n/a'
            if isinstance(uri, str) and uri.startswith('http'):
                st.markdown(f"- [{uri}]({uri}) — score: {score_text}")
            else:
                st.markdown(f"- {uri} — score: {score_text}")
    else:
        st.error("Request failed")

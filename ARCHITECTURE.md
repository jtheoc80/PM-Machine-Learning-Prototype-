# System Architecture

## Overview

The Pressure Relief Valve LLM Agent is designed as a modular system with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├─────────────────┬─────────────────┬───────────────────────────┤
│  CLI Interface  │  Web API (REST) │  Interactive Shell        │
│   (main.py)     │    (api.py)     │    (main.py)              │
└────────┬────────┴────────┬────────┴───────────┬───────────────┘
         │                 │                    │
         └─────────────────┼────────────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │     Core Application Logic         │
         │    (PressureValveAgent)            │
         └─────────────────┬──────────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
┌────────────────┐ ┌───────────────┐ ┌──────────────┐
│ Data Processor │ │   LLM Agent   │ │ Web Collector│
│ (data_processor│ │  (llm_agent.py│ │ (web_collector│
│      .py)      │ │       )       │ │     .py)     │
└────────┬───────┘ └───────┬───────┘ └──────┬───────┘
         │                 │                │
         │                 │                │
         ▼                 ▼                ▼
┌────────────────┐ ┌───────────────┐ ┌──────────────┐
│  File Uploads  │ │  Vector DB    │ │  Web Sources │
│  (CSV, JSON,   │ │  (ChromaDB)   │ │  (Internet)  │
│   TXT, etc.)   │ │               │ │              │
└────────────────┘ └───────────────┘ └──────────────┘
                           │
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
┌────────────────┐ ┌───────────────┐ ┌──────────────┐
│  Embeddings    │ │   Language    │ │   Retrieval  │
│  (Sentence     │ │   Model       │ │   System     │
│  Transformers) │ │  (HuggingFace)│ │  (LangChain) │
└────────────────┘ └───────────────┘ └──────────────┘
```

## Component Details

### 1. User Interfaces

#### CLI Interface (`main.py`)
- Command-line argument parsing
- Single-command execution
- Batch processing support

#### Interactive Shell (`main.py --interactive`)
- REPL-style interaction
- Session management
- Command history

#### Web API (`api.py`)
- RESTful endpoints
- FastAPI framework
- CORS support
- JSON request/response

### 2. Core Components

#### PressureValveAgent (`src/llm_agent.py`)
```
┌─────────────────────────────────────────┐
│        PressureValveAgent               │
├─────────────────────────────────────────┤
│ + __init__(model_name, embeddings)      │
│ + ingest_documents(docs, metadata)      │
│ + ingest_file(file_path)                │
│ + query(question) -> answer             │
│ + get_stats() -> statistics             │
├─────────────────────────────────────────┤
│ - llm: PressureValveLLM                 │
│ - embeddings: HuggingFaceEmbeddings     │
│ - vectorstore: ChromaDB                 │
│ - qa_chain: RetrievalQA                 │
└─────────────────────────────────────────┘
```

#### Data Processor (`src/data_processor.py`)
```
┌─────────────────────────────────────────┐
│         DataProcessor                   │
├─────────────────────────────────────────┤
│ + process_file(path) -> documents       │
│ + process_csv_file(path) -> docs        │
│ + process_json_file(path) -> docs       │
│ + process_text_file(path) -> docs       │
│ + save_upload(content, filename)        │
│ + list_uploads() -> file_list           │
└─────────────────────────────────────────┘
```

#### Web Collector (`src/web_collector.py`)
```
┌─────────────────────────────────────────┐
│        WebDataCollector                 │
├─────────────────────────────────────────┤
│ + search_web(query) -> results          │
│ + fetch_url_content(url) -> content     │
│ + collect_valve_information() -> docs   │
│ + get_technical_documentation() -> docs │
└─────────────────────────────────────────┘
```

### 3. Data Flow

#### Document Ingestion Flow
```
User Upload → File Save → Format Detection → Parser Selection
                                                    ↓
                                            Text Extraction
                                                    ↓
                                            Text Chunking
                                                    ↓
                                            Embedding Generation
                                                    ↓
                                            Vector Store Save
```

#### Query Processing Flow
```
User Query → Query Embedding → Vector Search → Document Retrieval
                                                       ↓
                                               Context Assembly
                                                       ↓
                                               LLM Generation
                                                       ↓
                                               Response + Sources
```

### 4. Storage Architecture

#### File System
```
project_root/
├── data/
│   ├── uploads/          # User uploaded files
│   ├── cache/            # Web content cache
│   └── chroma_db/        # Vector database
├── models/               # Downloaded/fine-tuned models
└── logs/                 # Application logs
```

#### Vector Database (ChromaDB)
- Stores document embeddings (384-dimensional vectors)
- Supports semantic similarity search
- Persistent storage with automatic indexing
- Metadata filtering capabilities

### 5. Dependencies

#### Core ML/AI
- `transformers`: Language model inference
- `torch`: Neural network backend
- `sentence-transformers`: Text embeddings
- `langchain`: LLM orchestration

#### Data Processing
- `pandas`: Structured data handling
- `numpy`: Numerical operations

#### Web & API
- `fastapi`: Web API framework
- `beautifulsoup4`: Web scraping
- `requests`: HTTP client

#### Storage
- `chromadb`: Vector database
- `faiss-cpu`: Vector similarity search

## Configuration

System behavior is controlled through:

1. **config.yaml**: Main configuration file
   - Model selection
   - Path configurations
   - Performance parameters

2. **Environment variables**: Runtime overrides
   - API keys
   - Custom paths
   - Debug settings

## Extensibility

### Adding New Data Sources
1. Create processor in `src/data_processor.py`
2. Register file extension mapping
3. Implement text extraction logic

### Adding New Models
1. Specify HuggingFace model ID
2. Update `config.yaml` or use `--model` flag
3. Ensure compatible with `transformers` library

### Custom Embeddings
1. Choose alternative sentence-transformers model
2. Update `EMBEDDINGS_MODEL` in config
3. Rebuild vector database

## Performance Considerations

### Memory Usage
- Base model (GPT-2): ~500MB RAM
- Embeddings: ~100MB RAM
- Vector store: Scales with document count
- Per query: ~50-100MB temporary

### Speed
- Model loading: One-time (10-30s)
- Document ingestion: ~1s per 100 documents
- Query processing: 2-5s per query
- Embedding generation: ~0.1s per document

### Scaling
- Horizontal: Multiple API instances
- Vertical: GPU acceleration for inference
- Storage: Distributed vector databases
- Caching: Redis for frequent queries

## Security

### API Security
- CORS configuration
- Rate limiting (recommended)
- API key authentication (to be added)
- Input validation

### Data Privacy
- Local processing (no external API calls for LLM)
- Encrypted storage (optional)
- Access control (to be implemented)

## Monitoring

### Logging
- Application logs: `logs/`
- Error tracking
- Query analytics
- Performance metrics

### Health Checks
- API endpoint: `/api/health`
- Model status
- Vector store connectivity
- Disk space monitoring

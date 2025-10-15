"""
Web API for Pressure Relief Valve LLM Agent

Provides a REST API using FastAPI for web-based interaction
"""

import os
import sys
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_agent import PressureValveAgent, create_agent
from src.data_processor import DataProcessor
from src.web_collector import WebDataCollector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pressure Relief Valve Expert API",
    description="API for the Pressure Relief Valve LLM Agent",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
agent: Optional[PressureValveAgent] = None
data_processor: Optional[DataProcessor] = None
web_collector: Optional[WebDataCollector] = None


# Request/Response Models
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []


class StatsResponse(BaseModel):
    model_name: str
    documents_count: int
    vectorstore_path: str


class StatusResponse(BaseModel):
    status: str
    message: str


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent, data_processor, web_collector
    
    logger.info("Starting Pressure Valve Expert API...")
    
    try:
        agent = create_agent(model_name="gpt2")
        data_processor = DataProcessor()
        web_collector = WebDataCollector()
        
        logger.info("API started successfully")
    except Exception as e:
        logger.error(f"Error starting API: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pressure Relief Valve Expert API",
        "version": "0.1.0",
        "endpoints": {
            "query": "/api/query",
            "upload": "/api/upload",
            "collect": "/api/collect",
            "stats": "/api/stats"
        }
    }


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the LLM agent with a question
    
    Args:
        request: Query request containing the question
        
    Returns:
        Answer and source documents
    """
    try:
        logger.info(f"Processing query: {request.question}")
        
        result = agent.query(request.question)
        
        # Extract source information
        sources = []
        for doc in result.get('source_documents', []):
            if hasattr(doc, 'metadata'):
                source = doc.metadata.get('source', 'Unknown')
                sources.append(source)
        
        return QueryResponse(
            answer=result['answer'],
            sources=list(set(sources))  # Remove duplicates
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload", response_model=StatusResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a dataset file
    
    Args:
        file: File to upload
        
    Returns:
        Status message
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Save the file
        file_content = await file.read()
        file_path = data_processor.save_upload(file_content, file.filename)
        
        # Process and ingest
        documents = data_processor.process_file(file_path)
        metadata = [{'source': file.filename, 'type': 'uploaded_dataset'}] * len(documents)
        agent.ingest_documents(documents, metadata)
        
        return StatusResponse(
            status="success",
            message=f"Successfully uploaded and processed {len(documents)} documents"
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/collect", response_model=StatusResponse)
async def collect_web_data(topics: Optional[List[str]] = None):
    """
    Collect data from the internet
    
    Args:
        topics: Optional list of topics to search for
        
    Returns:
        Status message
    """
    try:
        logger.info("Collecting web data...")
        
        # Get technical documentation
        docs = web_collector.get_technical_documentation()
        
        # Optionally collect specific topics
        if topics:
            web_docs = web_collector.collect_valve_information(topics)
            docs.extend(web_docs)
        
        # Ingest documents
        metadata = [{'source': 'web', 'type': 'technical_documentation'}] * len(docs)
        agent.ingest_documents(docs, metadata)
        
        return StatusResponse(
            status="success",
            message=f"Successfully collected and processed {len(docs)} documents"
        )
        
    except Exception as e:
        logger.error(f"Error collecting web data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics
    
    Returns:
        System statistics
    """
    try:
        stats = agent.get_stats()
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

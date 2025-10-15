"""
Core LLM Agent for Pressure Relief Valve Subject Matter Expertise

This module implements a specialized LLM agent that can:
1. Learn from uploaded datasets about pressure relief valves
2. Gather and integrate relevant data from the internet
3. Provide expert responses on pressure relief valve topics
"""

import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.docstore.document import Document
    from langchain.chains import RetrievalQA
    from langchain.llms.base import LLM
except ImportError:
    # Fallback for older langchain versions
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.docstore.document import Document
    from langchain.chains import RetrievalQA
    from langchain.llms.base import LLM
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PressureValveLLM(LLM):
    """
    Custom LLM wrapper for pressure relief valve expertise.
    Uses HuggingFace transformers for local inference.
    """
    
    model_name: str = "gpt2"  # Default lightweight model
    model: Any = None
    tokenizer: Any = None
    pipeline: Any = None
    max_length: int = 512
    temperature: float = 0.7
    
    def __init__(self, model_name: str = "gpt2", **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the language model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=self.max_length,
                temperature=self.temperature,
                do_sample=True,
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate text from the model"""
        try:
            result = self.pipeline(prompt, max_new_tokens=256, num_return_sequences=1)
            generated_text = result[0]["generated_text"]
            
            # Remove the prompt from the generated text
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "pressure_valve_llm"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return identifying parameters"""
        return {
            "model_name": self.model_name,
            "max_length": self.max_length,
            "temperature": self.temperature
        }


class PressureValveAgent:
    """
    Main agent class for pressure relief valve expertise.
    Handles data ingestion, vector storage, and question answering.
    """
    
    def __init__(
        self,
        model_name: str = "gpt2",
        embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        persist_directory: str = "./data/chroma_db"
    ):
        """
        Initialize the Pressure Valve Agent
        
        Args:
            model_name: Name of the HuggingFace model to use
            embeddings_model: Name of the embeddings model
            persist_directory: Directory to persist vector database
        """
        self.model_name = model_name
        self.persist_directory = persist_directory
        
        logger.info("Initializing Pressure Valve Agent...")
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_model,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize LLM
        self.llm = PressureValveLLM(model_name=model_name)
        
        # Initialize or load vector store
        self.vectorstore = self._initialize_vectorstore()
        
        # Initialize QA chain
        self.qa_chain = None
        if self.vectorstore:
            self._setup_qa_chain()
        
        logger.info("Agent initialized successfully")
    
    def _initialize_vectorstore(self) -> Optional[Chroma]:
        """Initialize or load existing vector store"""
        try:
            if os.path.exists(self.persist_directory):
                logger.info("Loading existing vector store...")
                return Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Creating new vector store...")
                os.makedirs(self.persist_directory, exist_ok=True)
                return Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            return None
    
    def _setup_qa_chain(self):
        """Setup the question-answering chain"""
        try:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            logger.info("QA chain setup complete")
        except Exception as e:
            logger.error(f"Error setting up QA chain: {e}")
    
    def ingest_documents(self, documents: List[str], metadata: Optional[List[Dict]] = None):
        """
        Ingest documents into the vector store
        
        Args:
            documents: List of document texts
            metadata: Optional list of metadata dictionaries for each document
        """
        try:
            logger.info(f"Ingesting {len(documents)} documents...")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            # Create Document objects
            docs = []
            for i, doc_text in enumerate(documents):
                meta = metadata[i] if metadata and i < len(metadata) else {}
                chunks = text_splitter.split_text(doc_text)
                for chunk in chunks:
                    docs.append(Document(page_content=chunk, metadata=meta))
            
            # Add to vector store
            if docs:
                self.vectorstore.add_documents(docs)
                self.vectorstore.persist()
                logger.info(f"Successfully ingested {len(docs)} document chunks")
                
                # Recreate QA chain with updated vectorstore
                self._setup_qa_chain()
            else:
                logger.warning("No documents to ingest")
                
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            raise
    
    def ingest_file(self, file_path: str):
        """
        Ingest a single file into the knowledge base
        
        Args:
            file_path: Path to the file to ingest
        """
        try:
            logger.info(f"Ingesting file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path)
            }
            
            self.ingest_documents([content], [metadata])
            logger.info(f"File ingested successfully: {file_path}")
            
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            raise
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the agent with a question about pressure relief valves
        
        Args:
            question: The question to ask
            
        Returns:
            Dictionary containing the answer and source documents
        """
        try:
            logger.info(f"Processing query: {question}")
            
            if not self.qa_chain:
                # Fallback to direct LLM if no knowledge base
                logger.warning("No knowledge base available, using direct LLM")
                answer = self.llm(f"Question about pressure relief valves: {question}\nAnswer:")
                return {
                    "answer": answer,
                    "source_documents": []
                }
            
            # Query the knowledge base
            result = self.qa_chain({"query": question})
            
            return {
                "answer": result.get("result", ""),
                "source_documents": result.get("source_documents", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "source_documents": []
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            if self.vectorstore:
                collection = self.vectorstore._collection
                count = collection.count() if hasattr(collection, 'count') else 0
                return {
                    "model_name": self.model_name,
                    "documents_count": count,
                    "vectorstore_path": self.persist_directory
                }
            return {
                "model_name": self.model_name,
                "documents_count": 0,
                "vectorstore_path": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


def create_agent(
    model_name: str = "gpt2",
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> PressureValveAgent:
    """
    Factory function to create a Pressure Valve Agent
    
    Args:
        model_name: Name of the language model to use
        embeddings_model: Name of the embeddings model to use
        
    Returns:
        Initialized PressureValveAgent instance
    """
    return PressureValveAgent(
        model_name=model_name,
        embeddings_model=embeddings_model
    )

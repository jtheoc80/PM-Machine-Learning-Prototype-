"""
Data Processing Utilities for Pressure Relief Valve Data

Handles various data formats and preprocessing for the LLM agent
"""

import os
import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes various data formats for ingestion into the LLM agent
    """
    
    def __init__(self, upload_dir: str = "./data/uploads"):
        """
        Initialize the data processor
        
        Args:
            upload_dir: Directory where uploaded files are stored
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def process_text_file(self, file_path: str) -> List[str]:
        """
        Process a text file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of document strings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by paragraphs if the file is large
            if len(content) > 5000:
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                return paragraphs
            else:
                return [content]
                
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            raise
    
    def process_csv_file(self, file_path: str) -> List[str]:
        """
        Process a CSV file containing pressure valve data
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of document strings (one per row)
        """
        try:
            df = pd.read_csv(file_path)
            
            documents = []
            for idx, row in df.iterrows():
                # Convert row to a readable text format
                doc_text = f"Record {idx + 1}:\n"
                for col in df.columns:
                    doc_text += f"{col}: {row[col]}\n"
                documents.append(doc_text)
            
            logger.info(f"Processed {len(documents)} records from CSV")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {e}")
            raise
    
    def process_json_file(self, file_path: str) -> List[str]:
        """
        Process a JSON file containing pressure valve data
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of document strings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                for idx, item in enumerate(data):
                    doc_text = f"Record {idx + 1}:\n{json.dumps(item, indent=2)}"
                    documents.append(doc_text)
            elif isinstance(data, dict):
                # If it's a single dictionary, convert to text
                doc_text = json.dumps(data, indent=2)
                documents.append(doc_text)
            else:
                documents.append(str(data))
            
            logger.info(f"Processed {len(documents)} records from JSON")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            raise
    
    def process_file(self, file_path: str) -> List[str]:
        """
        Process a file based on its extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of document strings
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        logger.info(f"Processing file: {file_path} (type: {extension})")
        
        if extension in ['.txt', '.md', '.rst']:
            return self.process_text_file(str(file_path))
        elif extension == '.csv':
            return self.process_csv_file(str(file_path))
        elif extension == '.json':
            return self.process_json_file(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def save_upload(self, file_content: bytes, filename: str) -> str:
        """
        Save an uploaded file
        
        Args:
            file_content: Content of the file as bytes
            filename: Name of the file
            
        Returns:
            Path to the saved file
        """
        try:
            file_path = self.upload_dir / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Saved upload: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving upload {filename}: {e}")
            raise
    
    def list_uploads(self) -> List[Dict[str, Any]]:
        """
        List all uploaded files
        
        Returns:
            List of file information dictionaries
        """
        try:
            files = []
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'extension': file_path.suffix
                    })
            return files
        except Exception as e:
            logger.error(f"Error listing uploads: {e}")
            return []


def create_sample_dataset(output_path: str = "./data/sample_pressure_valves.csv"):
    """
    Create a sample dataset for pressure relief valves for testing
    
    Args:
        output_path: Path where to save the sample dataset
    """
    sample_data = [
        {
            'valve_id': 'PRV-001',
            'type': 'Spring-loaded',
            'set_pressure_psi': 150,
            'capacity_gpm': 500,
            'manufacturer': 'Safety Corp',
            'material': 'Stainless Steel',
            'application': 'Steam System',
            'notes': 'Regular maintenance required every 6 months'
        },
        {
            'valve_id': 'PRV-002',
            'type': 'Pilot-operated',
            'set_pressure_psi': 300,
            'capacity_gpm': 1000,
            'manufacturer': 'Valve Tech Inc',
            'material': 'Carbon Steel',
            'application': 'Water System',
            'notes': 'High capacity for industrial use'
        },
        {
            'valve_id': 'PRV-003',
            'type': 'Balanced bellows',
            'set_pressure_psi': 200,
            'capacity_gpm': 750,
            'manufacturer': 'Safety Corp',
            'material': 'Brass',
            'application': 'Gas System',
            'notes': 'Suitable for corrosive environments'
        },
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv(output_path, index=False)
    logger.info(f"Sample dataset created at: {output_path}")
    return output_path

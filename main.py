"""
Main Application Interface for Pressure Relief Valve LLM Agent

Provides a command-line interface and API for interacting with the agent
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_agent import PressureValveAgent, create_agent
from src.data_processor import DataProcessor, create_sample_dataset
from src.web_collector import WebDataCollector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PressureValveApp:
    """
    Main application for the Pressure Relief Valve LLM Agent
    """
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize the application
        
        Args:
            model_name: Name of the language model to use
        """
        logger.info("Initializing Pressure Valve Expert System...")
        
        self.agent = create_agent(model_name=model_name)
        self.data_processor = DataProcessor()
        self.web_collector = WebDataCollector()
        
        logger.info("System initialized successfully")
    
    def upload_dataset(self, file_path: str):
        """
        Upload and process a dataset
        
        Args:
            file_path: Path to the dataset file
        """
        try:
            logger.info(f"Processing dataset: {file_path}")
            
            # Process the file
            documents = self.data_processor.process_file(file_path)
            
            # Ingest into the agent
            metadata = [{'source': file_path, 'type': 'uploaded_dataset'}] * len(documents)
            self.agent.ingest_documents(documents, metadata)
            
            logger.info(f"Successfully uploaded and processed dataset: {file_path}")
            print(f"\n✓ Dataset uploaded: {len(documents)} documents ingested\n")
            
        except Exception as e:
            logger.error(f"Error uploading dataset: {e}")
            print(f"\n✗ Error uploading dataset: {e}\n")
    
    def collect_web_data(self, topics: list = None):
        """
        Collect relevant data from the internet
        
        Args:
            topics: Optional list of topics to search for
        """
        try:
            logger.info("Collecting data from the web...")
            print("\nCollecting data from the internet...")
            
            # Get technical documentation
            docs = self.web_collector.get_technical_documentation()
            
            # Optionally collect more specific data
            if topics:
                web_docs = self.web_collector.collect_valve_information(topics)
                docs.extend(web_docs)
            
            # Ingest into the agent
            metadata = [{'source': 'web', 'type': 'technical_documentation'}] * len(docs)
            self.agent.ingest_documents(docs, metadata)
            
            logger.info(f"Collected and ingested {len(docs)} documents from the web")
            print(f"✓ Collected {len(docs)} documents from the internet\n")
            
        except Exception as e:
            logger.error(f"Error collecting web data: {e}")
            print(f"✗ Error collecting web data: {e}\n")
    
    def query(self, question: str):
        """
        Query the agent
        
        Args:
            question: The question to ask
        """
        try:
            logger.info(f"Processing query: {question}")
            
            result = self.agent.query(question)
            
            print(f"\nQuestion: {question}")
            print(f"\nAnswer: {result['answer']}")
            
            if result.get('source_documents'):
                print(f"\nSources used: {len(result['source_documents'])} documents")
            
            print()
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\n✗ Error: {e}\n")
    
    def show_stats(self):
        """Display system statistics"""
        stats = self.agent.get_stats()
        
        print("\n=== System Statistics ===")
        print(f"Model: {stats.get('model_name', 'N/A')}")
        print(f"Documents in knowledge base: {stats.get('documents_count', 0)}")
        print(f"Vector store location: {stats.get('vectorstore_path', 'N/A')}")
        print()
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("\n" + "="*60)
        print("  Pressure Relief Valve Expert System")
        print("  Type 'help' for commands, 'quit' to exit")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input(">> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'stats':
                    self.show_stats()
                
                elif user_input.lower().startswith('upload '):
                    file_path = user_input[7:].strip()
                    self.upload_dataset(file_path)
                
                elif user_input.lower() == 'collect':
                    self.collect_web_data()
                
                else:
                    # Treat as a question
                    self.query(user_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\n✗ Error: {e}\n")
    
    def show_help(self):
        """Show help information"""
        print("""
Available Commands:
  upload <file_path>  - Upload and process a dataset file
  collect             - Collect data from the internet
  stats               - Show system statistics
  help                - Show this help message
  quit/exit/q         - Exit the program
  
  Any other input will be treated as a question to the agent.
  
Examples:
  >> upload ./data/sample_pressure_valves.csv
  >> collect
  >> What are the types of pressure relief valves?
  >> How do I size a pressure relief valve?
  >> stats
        """)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pressure Relief Valve Expert System"
    )
    parser.add_argument(
        '--model',
        default='gpt2',
        help='Language model to use (default: gpt2)'
    )
    parser.add_argument(
        '--upload',
        help='Upload a dataset file'
    )
    parser.add_argument(
        '--collect',
        action='store_true',
        help='Collect data from the internet'
    )
    parser.add_argument(
        '--query',
        help='Ask a question'
    )
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create a sample dataset for testing'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    # Create sample dataset if requested
    if args.create_sample:
        sample_path = create_sample_dataset()
        print(f"Sample dataset created at: {sample_path}")
        return
    
    # Initialize the app
    app = PressureValveApp(model_name=args.model)
    
    # Handle commands
    if args.upload:
        app.upload_dataset(args.upload)
    
    if args.collect:
        app.collect_web_data()
    
    if args.query:
        app.query(args.query)
    
    # Run interactive mode if specified or if no other commands
    if args.interactive or not (args.upload or args.collect or args.query):
        app.interactive_mode()


if __name__ == '__main__':
    main()

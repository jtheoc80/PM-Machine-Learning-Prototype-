"""
Example/Demo Script for Pressure Relief Valve LLM Agent

Demonstrates the capabilities of the system
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_agent import create_agent
from src.data_processor import DataProcessor, create_sample_dataset
from src.web_collector import WebDataCollector


def demo():
    """Run a demonstration of the system"""
    
    print("="*70)
    print("  Pressure Relief Valve LLM Agent - Demonstration")
    print("="*70)
    print()
    
    # Step 1: Create sample data
    print("Step 1: Creating sample dataset...")
    sample_path = create_sample_dataset()
    print(f"✓ Sample dataset created at: {sample_path}\n")
    
    # Step 2: Initialize the agent
    print("Step 2: Initializing the LLM agent...")
    print("(This may take a minute as the model loads...)")
    agent = create_agent(model_name="gpt2")
    print("✓ Agent initialized\n")
    
    # Step 3: Load sample data
    print("Step 3: Loading sample dataset...")
    processor = DataProcessor()
    documents = processor.process_file(sample_path)
    metadata = [{'source': sample_path, 'type': 'sample_data'}] * len(documents)
    agent.ingest_documents(documents, metadata)
    print(f"✓ Loaded {len(documents)} documents\n")
    
    # Step 4: Load technical documentation
    print("Step 4: Loading technical documentation...")
    web_collector = WebDataCollector()
    tech_docs = web_collector.get_technical_documentation()
    tech_metadata = [{'source': 'technical_docs', 'type': 'documentation'}] * len(tech_docs)
    agent.ingest_documents(tech_docs, tech_metadata)
    print(f"✓ Loaded {len(tech_docs)} technical documents\n")
    
    # Step 5: Show statistics
    print("Step 5: System Statistics")
    stats = agent.get_stats()
    print(f"  Model: {stats.get('model_name', 'N/A')}")
    print(f"  Documents: {stats.get('documents_count', 0)}")
    print(f"  Vector Store: {stats.get('vectorstore_path', 'N/A')}")
    print()
    
    # Step 6: Demo queries
    print("Step 6: Example Queries")
    print("-" * 70)
    
    demo_questions = [
        "What are the main types of pressure relief valves?",
        "How should pressure relief valves be maintained?",
        "What factors are important for valve sizing?",
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\nQuery {i}: {question}")
        print()
        result = agent.query(question)
        print(f"Answer: {result['answer'][:300]}...")  # Truncate for demo
        if result.get('source_documents'):
            print(f"(Based on {len(result['source_documents'])} source documents)")
        print()
    
    print("="*70)
    print("  Demo Complete!")
    print("  Run 'python main.py --interactive' to try it yourself")
    print("="*70)


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()

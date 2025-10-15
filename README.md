# Pressure Relief Valve LLM Expert System

A specialized Large Language Model (LLM) agent for pressure relief valve expertise. This system can learn from uploaded datasets and integrate relevant information from the internet to provide expert guidance on pressure relief valves.

## Features

- 🤖 **Specialized LLM Agent**: Custom-trained language model focused on pressure relief valve knowledge
- 📊 **Dataset Upload**: Support for large datasets in multiple formats (CSV, JSON, TXT, Markdown)
- 🌐 **Web Data Collection**: Automatic collection of relevant technical information from the internet
- 💬 **Interactive Q&A**: Ask questions and get expert responses based on ingested knowledge
- 📚 **Vector Database**: Efficient storage and retrieval of technical documentation using embeddings
- 🔍 **Source Attribution**: Track which documents were used to answer questions

## Architecture

The system consists of several key components:

1. **LLM Agent** (`src/llm_agent.py`): Core language model using HuggingFace transformers
2. **Data Processor** (`src/data_processor.py`): Handles various data formats and preprocessing
3. **Web Collector** (`src/web_collector.py`): Gathers relevant information from the internet
4. **Vector Store**: Uses ChromaDB for efficient document storage and retrieval
5. **Main Application** (`main.py`): Command-line and interactive interface

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jtheoc80/PM-Machine-Learning-Prototype-.git
cd PM-Machine-Learning-Prototype-
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. **Create a sample dataset** (for testing):
```bash
python main.py --create-sample
```

2. **Run in interactive mode**:
```bash
python main.py --interactive
```

3. **Upload a dataset**:
```bash
python main.py --upload ./data/sample_pressure_valves.csv
```

4. **Collect web data**:
```bash
python main.py --collect
```

5. **Ask a question**:
```bash
python main.py --query "What are the types of pressure relief valves?"
```

### Interactive Mode

The interactive mode provides a command-line interface:

```
>> upload ./data/sample_pressure_valves.csv
>> collect
>> What is the proper way to size a pressure relief valve?
>> How often should pressure relief valves be maintained?
>> stats
>> quit
```

### Available Commands

- `upload <file_path>` - Upload and process a dataset file
- `collect` - Collect technical documentation from the internet
- `stats` - Show system statistics
- `help` - Show available commands
- `quit/exit/q` - Exit the program
- Any other input is treated as a question to the agent

### Supported File Formats

- **CSV** (`.csv`): Tabular data with headers
- **JSON** (`.json`): Structured data (objects or arrays)
- **Text** (`.txt`, `.md`, `.rst`): Plain text or markdown documents

## Configuration

Edit `config.yaml` to customize:

- Model selection (change to other HuggingFace models)
- Path configurations
- LLM parameters (temperature, max length, etc.)
- Vector store settings
- Web collection settings

## Advanced Usage

### Using a Different Model

You can specify a different HuggingFace model:

```bash
python main.py --model "distilgpt2" --interactive
```

For better performance, consider larger models like:
- `gpt2-medium`, `gpt2-large`, `gpt2-xl`
- `facebook/opt-1.3b`, `facebook/opt-2.7b`
- `EleutherAI/gpt-neo-1.3B`, `EleutherAI/gpt-neo-2.7B`

Note: Larger models require more memory and processing power.

### Programmatic Usage

```python
from src.llm_agent import create_agent
from src.data_processor import DataProcessor

# Initialize the agent
agent = create_agent(model_name="gpt2")

# Process and upload data
processor = DataProcessor()
documents = processor.process_file("./data/my_dataset.csv")
agent.ingest_documents(documents)

# Query the agent
result = agent.query("What are safety considerations for pressure relief valves?")
print(result['answer'])
```

## Project Structure

```
PM-Machine-Learning-Prototype-/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── llm_agent.py          # Core LLM agent implementation
│   ├── data_processor.py     # Data processing utilities
│   └── web_collector.py      # Web data collection
├── data/
│   ├── uploads/              # Uploaded dataset files
│   ├── cache/                # Cached web content
│   └── chroma_db/            # Vector database storage
├── models/                    # Saved model files
├── logs/                      # Application logs
├── main.py                    # Main application interface
├── config.yaml                # Configuration file
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Technical Details

### Vector Embeddings

The system uses sentence transformers to create embeddings of documents, which are stored in a ChromaDB vector database. This enables semantic search and retrieval of relevant information.

### LLM Integration

The agent uses HuggingFace transformers library with a custom LLM wrapper that integrates with LangChain for:
- Document retrieval
- Question answering
- Context-aware responses

### Data Processing Pipeline

1. **Ingestion**: Files are uploaded and processed based on their format
2. **Chunking**: Large documents are split into manageable chunks
3. **Embedding**: Text chunks are converted to vector embeddings
4. **Storage**: Embeddings are stored in the vector database
5. **Retrieval**: Relevant chunks are retrieved for each query
6. **Generation**: LLM generates answers based on retrieved context

## Troubleshooting

### Out of Memory Errors

If you encounter memory errors with larger models:
- Use a smaller model (e.g., `distilgpt2`)
- Reduce `CHUNK_SIZE` in `config.yaml`
- Process datasets in smaller batches

### Slow Performance

To improve performance:
- Use GPU if available (install `torch` with CUDA support)
- Reduce `MAX_LENGTH` parameter
- Use a smaller embeddings model

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [HuggingFace Transformers](https://huggingface.co/transformers/)
- Uses [LangChain](https://www.langchain.com/) for LLM orchestration
- Vector storage powered by [ChromaDB](https://www.trychroma.com/)

## Contact

For questions or support, please open an issue on GitHub 

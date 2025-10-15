# Quick Start Guide

## 5-Minute Setup

### Option 1: Automated Setup (Linux/Mac)

```bash
# Run the setup script
./setup.sh

# Activate the virtual environment
source venv/bin/activate

# Run the demo
python demo.py
```

### Option 2: Manual Setup (All platforms)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run demo
python demo.py
```

## First Steps

### 1. Try the Demo
```bash
python demo.py
```
This will show you what the system can do.

### 2. Create Sample Data
```bash
python main.py --create-sample
```

### 3. Interactive Mode
```bash
python main.py --interactive
```

Then try:
```
>> upload ./data/sample_pressure_valves.csv
>> collect
>> What are the types of pressure relief valves?
>> quit
```

### 4. Start the Web API
```bash
python api.py
```

Then open http://localhost:8000 in your browser.

## Common Commands

### Upload Data
```bash
python main.py --upload mydata.csv
```

### Ask Questions
```bash
python main.py --query "How do I size a pressure relief valve?"
```

### Collect Web Data
```bash
python main.py --collect
```

### Check Status
```bash
python main.py --interactive
>> stats
```

## Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt --upgrade
```

### Slow or Out of Memory
```bash
# Use a smaller model
python main.py --model distilgpt2 --interactive
```

### Need Help
- Check [README.md](README.md) for detailed documentation
- Check [TESTING.md](TESTING.md) for testing guide
- Check the [GitHub repository](https://github.com/jtheoc80/PM-Machine-Learning-Prototype-) for issues

## Next Steps

1. **Add Real Data**: Upload your own pressure relief valve datasets
2. **Customize**: Edit `config.yaml` to change settings
3. **Integrate**: Use the API (`api.py`) in your applications
4. **Expand**: Add more technical documentation to improve answers

## Tips

- Start with small datasets to get familiar
- Use `--collect` to add technical knowledge
- The more data you add, the better the answers
- Check `stats` regularly to see what's loaded
- Use GPU if available for better performance

## File Formats Supported

- **CSV** - Tables with headers
- **JSON** - Structured data
- **TXT/MD** - Plain text documentation

## Example Queries

- "What are the main types of pressure relief valves?"
- "How do I maintain a pressure relief valve?"
- "What standards apply to pressure relief valves?"
- "How do I calculate the required relief capacity?"
- "What are common failure modes?"

Enjoy using the Pressure Relief Valve Expert System!

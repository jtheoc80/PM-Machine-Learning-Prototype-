# Testing Guide for Pressure Relief Valve LLM Agent

## Quick Test

The fastest way to test the system is to run the demo:

```bash
python demo.py
```

This will:
1. Create a sample dataset
2. Initialize the LLM agent
3. Load sample data and technical documentation
4. Run example queries
5. Display results

## Manual Testing

### 1. Test Sample Dataset Creation

```bash
python main.py --create-sample
```

Expected output: Message confirming sample dataset created at `./data/sample_pressure_valves.csv`

### 2. Test Interactive Mode

```bash
python main.py --interactive
```

Then try these commands:
- `help` - Should display available commands
- `stats` - Should show system statistics
- `upload ./data/sample_pressure_valves.csv` - Should upload the sample data
- `collect` - Should collect technical documentation
- `What are the types of pressure relief valves?` - Should provide an answer
- `quit` - Exit the program

### 3. Test Direct Query

```bash
python main.py --query "What is a pressure relief valve?"
```

Expected: The agent should respond with information (note: without uploaded data, it will use only the base model knowledge)

### 4. Test Data Upload and Query

```bash
# First create sample data
python main.py --create-sample

# Upload the sample data
python main.py --upload ./data/sample_pressure_valves.csv

# Collect web data
python main.py --collect

# Query with context
python main.py --query "What valve types are in the dataset?"
```

### 5. Test Web API

Start the API server:
```bash
python api.py
```

In another terminal, test endpoints:

```bash
# Health check
curl http://localhost:8000/api/health

# Get stats
curl http://localhost:8000/api/stats

# Collect data
curl -X POST http://localhost:8000/api/collect

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are pressure relief valve types?"}'

# Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@./data/sample_pressure_valves.csv"
```

## Test Data Formats

### Test CSV Upload

Create `test_data.csv`:
```csv
valve_id,type,pressure,notes
V001,Spring-loaded,150,Standard valve
V002,Pilot-operated,300,High capacity
```

Upload:
```bash
python main.py --upload test_data.csv
```

### Test JSON Upload

Create `test_data.json`:
```json
[
  {
    "valve_id": "V001",
    "type": "Spring-loaded",
    "pressure_psi": 150
  },
  {
    "valve_id": "V002",
    "type": "Pilot-operated",
    "pressure_psi": 300
  }
]
```

Upload:
```bash
python main.py --upload test_data.json
```

### Test Text Upload

Create `test_data.txt`:
```
Pressure relief valves are critical safety devices.

They protect systems from overpressure conditions.

Regular maintenance is essential for proper operation.
```

Upload:
```bash
python main.py --upload test_data.txt
```

## Expected Behaviors

### Successful Operation

- No Python exceptions or errors
- Clear output messages
- Statistics show increasing document counts after uploads
- Queries return relevant answers
- API endpoints return JSON responses

### Known Limitations

1. **First Run**: Model download may take time (especially larger models)
2. **Memory**: Default GPT-2 model is small; larger models need more RAM
3. **Accuracy**: Responses depend on uploaded data quality
4. **Web Collection**: Limited by internet connectivity and website accessibility

## Troubleshooting

### Import Errors

If you see import errors:
```bash
pip install -r requirements.txt --upgrade
```

### Memory Errors

If running out of memory:
1. Use smaller model: `python main.py --model distilgpt2`
2. Reduce chunk size in config.yaml
3. Process files individually rather than in batch

### Slow Responses

This is normal for:
- First query (model initialization)
- Large datasets
- Complex queries

To improve:
- Use GPU if available
- Reduce MAX_LENGTH in config.yaml
- Use lighter models

### No Answers or Generic Answers

If responses are too generic:
1. Ensure data is uploaded: `python main.py --upload <file>`
2. Collect web data: `python main.py --collect`
3. Check stats to verify documents are loaded

## Validation Checklist

- [ ] Setup script runs without errors
- [ ] Demo runs and completes
- [ ] Can create sample dataset
- [ ] Can run interactive mode
- [ ] Can upload CSV files
- [ ] Can upload JSON files
- [ ] Can upload text files
- [ ] Can collect web data
- [ ] Can query the agent
- [ ] Stats show correct document count
- [ ] API starts successfully
- [ ] API health check works
- [ ] API query endpoint works
- [ ] API upload endpoint works

## Performance Benchmarks

On a typical laptop (16GB RAM, no GPU):

- Model initialization: 10-30 seconds
- Sample data upload: 1-2 seconds
- Web data collection: 5-10 seconds
- Query response: 2-5 seconds
- Large dataset (1000 rows): 30-60 seconds

## Next Steps

After successful testing:

1. **Add Your Own Data**: Upload real pressure relief valve datasets
2. **Customize Model**: Try different HuggingFace models for better results
3. **Expand Knowledge**: Add more technical documentation
4. **Integrate**: Use the API for web applications
5. **Fine-tune**: Consider fine-tuning models on your specific domain data

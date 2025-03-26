# Screen Monitor Server

## Overview
This is a Python-based server that:
- Captures screenshots at regular intervals
- Processes screenshots through a local LLM (Ollama)
- Provides API endpoints to retrieve screenshots and descriptions

## Prerequisites
- Python 3.8+
- Ollama installed and running
- Llava model pulled in Ollama

## Installation
1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Ollama is running with Llava model:
```bash
ollama pull llava
```

## Configuration
Edit `config.yaml` to customize:
- Screenshot interval
- Storage paths
- Server host/port
- LLM model

## Running the Server
```bash
python run.py
```

## API Endpoints
- `/screenshot/latest`: Get the most recent screenshot
- `/description/latest`: Get description of the latest screenshot
- `/descriptions`: List recent descriptions
- `/screenshot/{timestamp}`: Get a specific screenshot

## How It Works
1. Automatically captures screenshots at configured interval
2. Optionally processes screenshots through local LLM
3. Stores screenshots and descriptions
4. Provides API to access screenshots and descriptions

## Notes
- Requires Ollama running locally
- Uses Llava model for image description
- Screenshots are stored locally
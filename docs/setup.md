# Setup Guide

Follow these instructions to get the LegalDoc AI Engine and its documentation running locally for review.

## Prerequisites

* **Python**: 3.11 or higher
* **Environment**: A virtual environment is recommended (`python -m venv .venv`)
* **MkDocs**: The documentation site requires `mkdocs` and the `readthedocs` theme.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/diptu/doc-rag-engine
   cd doc-rag-engine
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file  similar to `env.example` file in the root directory and add your necessary API keys (e.g., OpenAI or Anthropic).

```text
   api_key=YOUR_OPENAI_API_KEY
```

## Running the Documentation

To view the architecture, pipeline details, and evaluation metrics in your browser:

```bash
mkdocs serve
```
Once started, navigate to **http://127.0.0.1:8000/doc-rag-engine/** to view the documentation site.

## Running the Application

To start the core RAG API server:
```bash
python -m app.main
```
Once started, navigate to `http://127.0.0.1:8001/docs` to view the api endpoints.
## Running Tests

The project includes a comprehensive suite of tests covering each module (OCR, Retrieval, Feedback).
```bash
pytest tests/
```

## Docker Deployment 

For a consistent reviewer experience, the system is fully containerized. This ensures all dependencies—including OCR libraries and data persistence—are handled automatically.

### Running with Docker Compose
The project uses Docker Compose to orchestrate the engine and its environment. Run the following command from the root directory:

```bash

docker compose up --build

```

### Data Persistence
The `data/` directory is mounted as a volume in the Docker configuration. This ensures that the **Vector Store index** and **Feedback logs** (crucial for the "Improvement from Edits" rubric) persist across container restarts.
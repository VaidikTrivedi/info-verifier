# Info-Verifier

## Overview

**Info-Verifier** is an automated fact-checking and content analysis system for news articles and claims. It leverages state-of-the-art language models (Google Gemini) and web search tools to decompose, investigate, and adjudicate the veracity of statements in a given text. The system is built using FastAPI for the backend, LangGraph for workflow orchestration, and integrates with DuckDuckGo for evidence gathering.

---

## Features

- **Automated Claim Extraction:** Breaks down input text into atomic, verifiable claims.
- **Web Evidence Gathering:** Uses DuckDuckGo to search for supporting or contradicting evidence.
- **AI-Powered Verification:** Employs Google Gemini models to analyze claims and evidence.
- **Structured Reporting:** Returns a detailed integrity report with confidence scores and reasoning.
- **Async API:** Submit articles for verification and poll for results using a job ID.

---

## System Architecture

- **FastAPI Backend:** Handles API requests and job management.
- **LangGraph Tribunal:** Orchestrates the decomposition, investigation, and judgment of claims.
- **Background Processing:** Jobs are processed asynchronously.
- **.env Configuration:** API keys and secrets are managed via environment variables.

---

## How It Works

1. **User submits a news article** via the `/verify` API endpoint.
2. **System decomposes** the article into atomic claims.
3. **Each claim is investigated** using web search for evidence.
4. **Claims are adjudicated** by the AI model, which returns a verdict and confidence score.
5. **A final report** is compiled and made available via the `/status/{job_id}` endpoint.

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/Info-Verifier.git
cd Info-Verifier
```

### 2. Create and Activate a Virtual Environment

```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your-google-gemini-api-key
```

> **Note:** You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Run the FastAPI Server

You can use the provided VS Code launch configuration or run manually:

```sh
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Usage

### Submit a News Article for Verification

Send a POST request to `/verify`:

```sh
curl -X POST http://127.0.0.1:8000/verify \
     -H "Content-Type: application/json" \
     -d '{"text": "Kashmir is an integral part of india"}'
```

Response:

```json
{
  "job_id": "123-abc",
  "message": "Verification started. Poll /status/{job_id} for results."
}
```

### Poll for Results

Send a GET request to `/status/{job_id}`:

```sh
curl http://127.0.0.1:8000/status/123-abc
```

---

## Testing

A sample test script is provided in `test-request.py`:

```sh
python test-request.py
```

This script:
- Submits a sample article for verification.
- Polls the status endpoint until the report is ready.
- Prints the final report.

---

## Project Structure

```
Info-Verifier/
├── main.py              # FastAPI app and endpoints
├── graph.py             # LangGraph workflow and AI logic
├── schemas.py           # Pydantic models for claims and reports
├── test-request.py      # Example client script
├── .env                 # API keys (not committed)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Notes

- For production, consider using Redis or a database for job storage.
- The current setup uses in-memory storage for simplicity.
- Ensure your API key has access to the Google Generative Language API.


---

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Generative AI](https://ai.google.dev/)
- [DuckDuckGo Search API](https://duckduckgo.com/)
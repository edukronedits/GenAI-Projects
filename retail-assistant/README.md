# Retail Assistant

Runnable FastAPI reference implementation for a multimodal retail copilot. It includes catalog search, product comparison-ready data, image upload validation with a vision adapter seam, support intent routing, source attribution, health checks, and a responsive web client.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Open http://localhost:8001. API docs are available at `/docs`.

The in-memory catalog is deliberately replaceable: `search_products` is the seam for BM25 + vector + RRF retrieval, and `vision` is the seam for a hosted vision model. Never connect transactional tools without authorization, timeouts, audit logging, and server-side validation.

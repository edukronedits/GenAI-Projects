# Agentic Banking Self-Service Assistant

A runnable FastAPI reference implementation for authenticated banking self-service. It separates knowledge answers from transactional workflows, requires an authenticated session, exposes tightly scoped action endpoints, and blocks high-impact actions behind explicit confirmation with a service reference.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

Open http://localhost:8003. The browser uses a demo session token. In production, replace it with an OIDC/MFA session, server-side authorization, idempotency keys, policy/risk services, durable audit events, and real banking API adapters. The LLM should only propose structured actions; it must never write to core banking data directly.

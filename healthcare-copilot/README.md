# Clinical Knowledge & Patient Care Copilot

A runnable FastAPI reference implementation for an authorization-first clinical copilot. It demonstrates patient-scope filtering before retrieval, deterministic lab trend summaries, approved guideline evidence, provenance, safety language, audit-oriented request boundaries, and a responsive clinician workspace.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Open http://localhost:8002. Use `X-Demo-User: viewer` to verify restricted patient and guideline access. Replace the in-memory repositories with FHIR/EHR adapters, enforce enterprise identity and audit persistence, and place the model behind a reviewed clinical safety policy before production use.

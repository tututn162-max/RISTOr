Technique Framework API (Spec-Compliant)

- FastAPI service implementing Calls 1-4 and ingestion per specification.
- Deterministic validator, patcher, finalizer, audit logs, and metrics.

Setup

- Python 3.13
- Install deps: `pip3 install -r /workspace/requirements.txt`
- Run tests: `pytest -q`
- Start server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Environment

- Optional Gemini: set `GEMINI_API_KEY` for semantic auditing.

Notes

- `audit/` stores append-only logs.
- `GET /metrics` returns in-memory metrics snapshot.
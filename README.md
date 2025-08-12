Technique Framework API (Spec-Compliant)

- FastAPI service implementing Calls 1-4 and ingestion per specification.
- Deterministic validator, patcher, finalizer, audit logs, and metrics.

Setup

- Python 3.11+ (Linux/macOS/Windows). For Python 3.13, use `pydantic==2.10+`.
- Install deps: `pip install -r requirements.txt`
- Windows: ensure project root is on `PYTHONPATH` (pytest config included) or run `set PYTHONPATH=.` in PowerShell.
- Run tests: `pytest -q`
- Start server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Environment

- Optional Gemini: set `GEMINI_API_KEY` for semantic auditing.
- Audit directory: set `AUDIT_DIR` or defaults to `./audit`.

Notes

- `audit/` stores append-only logs.
- `GET /metrics` returns in-memory metrics snapshot.
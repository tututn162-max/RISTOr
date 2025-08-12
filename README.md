## Technique Framework API (Spec-Compliant)

Implements Calls 1–4 and ingestion per the specification. Deterministic generation, strict validation, patching with diff + versioning, finalization with iteration limits, metrics, and append-only audit logs.

### Prerequisites
- Python 3.11+ (Linux/macOS/Windows). Python 3.13 is supported.
- pip available in your shell.

### Install
- From the project root:
```bash
pip install -r requirements.txt
```

### Configure (optional)
- Gemini API key for semantic audit (only used when invoked by callers):
  - Linux/macOS (bash/zsh): `export GEMINI_API_KEY="your-key"`
  - Windows PowerShell: `$env:GEMINI_API_KEY="your-key"`
  - Windows cmd.exe: `set GEMINI_API_KEY=your-key`
- Audit directory (default `./audit`):
  - `export AUDIT_DIR="/path/to/audit"` (or Windows equivalent)

### Run tests (what should happen)
- From the project root:
```bash
pytest -q
```
- Expected: all tests pass. Example: `7 passed in X.XXs`.

### Run the API server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- What should happen:
  - Server listens on port 8000.
  - `GET /metrics` returns counters and timings.
  - `audit/log.jsonl` starts recording immutable events.

### Quickstart: End-to-end workflow and expected outcomes
All calls are JSON over HTTP. Use curl or any REST client.

1) Call 1 — Generate
```bash
curl -s -X POST http://localhost:8000/generateTechnique \
  -H 'Content-Type: application/json' \
  -d '{
    "seed": "demo-seed-1",
    "request_id": "req-1",
    "name_uniqueness_required": true
  }'
```
- You get `{ machine_data, human_text }`.
- `human_text` strictly matches the template.
- `machine_data.machine_data_hash` is a SHA-256 of canonical JSON.
- Re-submitting the same `seed + request_id` returns the same content (deterministic).

2) Call 2 — Validate
```bash
curl -s -X POST http://localhost:8000/validateTechnique \
  -H 'Content-Type: application/json' \
  -d '{
    "machine_data": { ... },
    "human_text": "..."
  }'
```
- You get a `validation_report` with:
  - `pass: true|false`, `score: 0..100`, `criteria[]`, `total_errors`, `total_warnings`.
- If `pass==true` and `score>=95.0`, proceed to Finalize (Call 4). Otherwise, patch (Call 3).

3) Call 3 — Patch (auto-patch deterministic)
```bash
curl -s -X POST http://localhost:8000/patchTechnique \
  -H 'Content-Type: application/json' \
  -d '{
    "machine_data": { ... },
    "human_text": "...",
    "validation_report": { ... }
  }'
```
- What happens:
  - Auto-applies `criteria[].remediation.type=="auto_patch"` patches in order (error before warning, id lexical).
  - Updates `version`, `parent_hash`, `updated_at`, recomputes `machine_data_hash`.
  - Rebuilds `human_text` from machine data.
  - Returns `{ machine_data, human_text, diff, version, machine_data_hash, status: "patched" }`.
  - If patched data does not validate deterministically, returns `ERR_PATCH_VALIDATION_FAILED` (400).

4) Call 2 again — Re-Validate
- Repeat Call 2 with the patched data. If still failing and you remain under iteration limits, repeat Call 3.

5) Call 4 — Finalize
```bash
curl -s -X POST http://localhost:8000/finalizeTechnique \
  -H 'Content-Type: application/json' \
  -d '{
    "machine_data": { ... },
    "human_text": "...",
    "attempts_history": [ { "score": 98.0, "pass": true, ... } ]
  }'
```
- Expected outcomes:
  - If latest `score>=95.0` and `pass==true`, returns `final_state: "final_validated"`, `ingestion_ready: true`.
  - If iteration limit reached or non-convergent, returns `final_state: "manual_review"`.

6) Ingestion (separate contract)
```bash
curl -s -X POST http://localhost:8000/ingestTechnique \
  -H 'Content-Type: application/json' \
  -d '{
    "machine_data": { ... },
    "human_text": "..."
  }'
```
- The service verifies the hash matches the payload.
- On success, returns `ingestion_log_id`, `ingested_at`, `lore_entry_id`.

### Determinism and constraints (what to expect)
- `seed + request_id` → identical output for generation (including hash and `version=1`).
- The canonical core concept text is embedded verbatim in `machine_data.core_concept_text`.
- `human_text` is regenerated from `machine_data` and must match the exact template.
- Enums and numeric bounds are enforced strictly.

### Metrics
- `GET /metrics` returns a JSON snapshot like:
```json
{
  "counters": { "techniques_generated_total": 3 },
  "gauges": {},
  "timings_ms": { "generate_ms": [12.3], "validate_ms": [3.8] }
}
```

### Audit logs
- Default path: `./audit/log.jsonl` (set `AUDIT_DIR` to change).
- Each line is a JSON object: `{ ts, action, actor_id, payload }`.
- Actions include: `generate`, `validate`, `patch`, `finalize`, `ingest`.

### Gemini (semantic auditor)
- If `GEMINI_API_KEY` is set, the semantic auditor is available to callers that choose to invoke it (the deterministic validator runs regardless). When not set, the app returns empty audit findings and continues.

### Troubleshooting
- ModuleNotFoundError: No module named `app`
  - Ensure you run commands from the project root.
  - `pytest.ini` and `pyproject.toml` set `pythonpath=.`. If still needed, set env: `export PYTHONPATH=.` (PowerShell: `$env:PYTHONPATH='.'`).
- Pip install problems on Debian/Ubuntu (externally managed):
  - Prefer a virtualenv; or use the system’s recommended approach. Standard `pip install -r requirements.txt` typically suffices on Windows/macOS.
- Port conflicts: use a different port with `--port 8080`.

### Expected error handling
- On schema or hash mismatch, you receive a 400 with `error_code` and remediation hints.
- Patch failures return `ERR_PATCH_VALIDATION_FAILED`.
- Finalization with too many attempts returns `ERR_MAX_ITERATIONS_REACHED` and `final_state: manual_review`.

### Security & integrity (operational)
- All inputs are JSON; audit entries are append-only.
- `machine_data_hash` is recomputed on every change; used as an immutable key and for optimistic concurrency.
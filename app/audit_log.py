import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

AUDIT_DIR = "/workspace/audit"
AUDIT_FILE = os.path.join(AUDIT_DIR, "log.jsonl")

os.makedirs(AUDIT_DIR, exist_ok=True)


def append_audit(action: str, actor_id: str, payload: Dict[str, Any]) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "actor_id": actor_id,
        "payload": payload,
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":"), ensure_ascii=False) + "\n")
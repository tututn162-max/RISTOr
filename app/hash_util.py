import hashlib
import json
import re
from typing import Any, Dict


def canonical_json(obj: Dict[str, Any]) -> str:
    # Exclude machine_data_hash during hashing to avoid circularity if present
    data = {k: v for k, v in obj.items() if k != "machine_data_hash"}
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex_lower(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


_slug_regex_cleanup = re.compile(r"[^a-z0-9-]+")


def to_name_id(name: str) -> str:
    s = name.strip().lower().replace(" ", "-")
    s = s.replace("'", "-")
    s = _slug_regex_cleanup.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80]
from __future__ import annotations
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone
from .schemas import MachineData
from .hash_util import canonical_json, sha256_hex_lower
from .validator import validate, build_human_text


def apply_patches(machine_data: Dict[str, Any], criteria: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    modified_fields = {}
    # order by severity (error before warning), then by id lexicographically
    def sort_key(c):
        return (0 if c.get("severity") == "error" else 1, c.get("id", ""))

    for c in sorted(criteria, key=sort_key):
        rem = c.get("remediation", {})
        if not c.get("pass") and rem.get("type") == "auto_patch":
            patch = rem.get("patch_snippet", {})
            for k, v in patch.items():
                modified_fields[k] = v
    # apply
    new_md = {**machine_data, **modified_fields}
    return new_md, modified_fields


def patch(machine_data: Dict[str, Any], human_text: str, validation_report: Dict[str, Any]) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    # auto-apply patches
    new_md, modified_fields = apply_patches(machine_data, [c for c in validation_report.get("criteria", [])])

    # update metadata
    old_hash = machine_data.get("machine_data_hash")
    new_version = int(machine_data.get("version", 1)) + 1
    new_md["version"] = new_version
    new_md["parent_hash"] = old_hash
    new_md["updated_at"] = datetime.now(timezone.utc).isoformat()

    # recompute hash
    new_md["machine_data_hash"] = sha256_hex_lower(canonical_json(new_md))

    # rebuild human text to reflect machine fields minimally
    new_human = build_human_text(MachineData(**new_md))

    # produce diff
    diff = {"modified": [], "added": [], "removed": []}
    for k, new_v in modified_fields.items():
        old_v = machine_data.get(k)
        entry = {"field": k}
        if old_v is None:
            entry.update({"old": None, "new": new_v})
            diff["added"].append(entry)
        else:
            entry.update({"old": old_v, "new": new_v})
            diff["modified"].append(entry)

    # validate patched md deterministically
    vrep = validate(new_md, new_human)
    if not vrep.pass_:
        raise ValueError("ERR_PATCH_VALIDATION_FAILED")

    return new_md, new_human, diff
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict
from datetime import datetime, timezone
import re
import random

from .schemas import GenerateRequest, TechniqueEnvelope, ValidateInput, ValidationReport, PatchInput, PatchOutput, FinalizeInput, FinalizeOutput, MachineData
from .constants import (
    CORE_CONCEPT_TEXT,
    CORE_CONCEPT_ID,
    HUMAN_TEXT_TEMPLATE,
    TECHNIQUE_TYPES,
    POWER_OUTPUT_STATS,
    ACTIVATION_TIME_UNITS,
)
from .hash_util import sha256_hex_lower, canonical_json, to_name_id
from .validator import validate, build_human_text
from .patcher import patch
from .store import store, TechniqueRecord
from .metrics import metrics, time_block
from .audit_log import append_audit

app = FastAPI(title="Technique Framework API", version="1.0.0")


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()


def _deterministic_rng(seed: str, request_id: str) -> random.Random:
    key = sha256_hex_lower(seed + "|" + request_id)
    rnd = random.Random(int(key[:16], 16))
    return rnd


def _choose(rnd: random.Random, items: list[str]) -> str:
    return items[rnd.randrange(0, len(items))]


def _generate_name(rnd: random.Random) -> str:
    syllables = [
        "Iron", "Stone", "Bone", "Vein", "Pulse", "Core", "Fist", "Skin", "Frame", "Spine",
        "Stead", "Ward", "Shell", "Root", "Forge", "Anvil", "Stride", "Gale", "Sinew", "Bastion"
    ]
    a = _choose(rnd, syllables)
    b = _choose(rnd, syllables)
    while b == a:
        b = _choose(rnd, syllables)
    name = f"{a} {b}"
    # enforce regex by trimming if necessary
    return name[:60]


@app.post("/generateTechnique")
def generate_technique(req: GenerateRequest):
    with time_block("generate_ms"):
        rnd = _deterministic_rng(req.seed, req.request_id)

        base_name = _generate_name(rnd)
        name = base_name
        if req.name_uniqueness_required:
            ctr = 2
            while not store.is_name_unique(name):
                name = f"{base_name}-{ctr}"
                ctr += 1

        name_id = to_name_id(name)
        ttype = _choose(rnd, sorted(list(TECHNIQUE_TYPES)))
        stat = _choose(rnd, sorted(list(POWER_OUTPUT_STATS)))
        activation_unit = "seconds"
        power_output_pct = float(rnd.randrange(100, 151))
        qi_cost_percent = float(max(1, rnd.randrange(1, 31)))
        activation_time_value = round(rnd.random() * 5 + 0.1, 1)
        manifestation_tags = ["aura-shimmer", "muscle-swell"][: rnd.randrange(1, 3)]
        intended_application = ["dueling", "training", "endurance"][: rnd.randrange(1, 4)]
        special_properties = []
        drawbacks = ["induces muscle fatigue"]

        description = (
            "An internal body-forging technique that compacts Qi into muscles and bones to reinforce movement and impact without external projection."
        )
        effect = "Temporarily boosts {stat} via internal Qi compression; no external constructs.".replace("{stat}", stat)

        now = datetime.now(timezone.utc).isoformat()

        md = {
            "name": name,
            "name_id": name_id,
            "type": ttype,
            "core_concept_id": CORE_CONCEPT_ID,
            "core_concept_text": CORE_CONCEPT_TEXT,
            "description": description,
            "power_output_pct": power_output_pct,
            "power_output_stat": stat,
            "effect": effect,
            "manifestation_tags": manifestation_tags,
            "qi_cost_percent": qi_cost_percent,
            "activation_time_value": activation_time_value,
            "activation_time_unit": activation_unit,
            "intended_application": intended_application,
            "special_properties": special_properties,
            "drawbacks": drawbacks,
            "human_text": "",  # placeholder; filled after hash
            "machine_data_hash": "",
            "seed": req.seed,
            "request_id": req.request_id,
            "version": 1,
            "parent_hash": None,
            "created_at": now,
            "updated_at": now,
        }

        # build human text from md
        human_text = build_human_text(MachineData(**{**md, "human_text": "", "machine_data_hash": "dummy"}))
        md["human_text"] = human_text
        # compute hash over canonical JSON (excluding machine_data_hash)
        md["machine_data_hash"] = sha256_hex_lower(canonical_json(md))

        env = {"machine_data": md, "human_text": human_text}
        append_audit("generate", "system", {"request": req.model_dump(), "machine_data_hash": md["machine_data_hash"]})
        metrics.inc("techniques_generated_total")

        # persist in store
        store.save(TechniqueRecord(machine_data=md, human_text=human_text, status="generated", attempts_history=[]))

        return JSONResponse(env)


@app.post("/validateTechnique")
def validate_technique(payload: ValidateInput):
    with time_block("validate_ms"):
        vrep = validate(payload.machine_data.model_dump(), payload.human_text)
        status = "validated"
        rec = store.get_by_hash(payload.machine_data.machine_data_hash)
        if rec:
            rec.status = status
            rec.attempts_history.append(vrep.model_dump())
        append_audit("validate", "system", {"md_hash": payload.machine_data.machine_data_hash, "pass": vrep.pass_, "score": vrep.score})
        return JSONResponse(vrep.model_dump(by_alias=True))


@app.post("/patchTechnique")
def patch_technique(payload: PatchInput):
    with time_block("patch_ms"):
        # optimistic locking via parent_hash
        current = store.get_by_hash(payload.machine_data.machine_data_hash)
        # We accept patching the provided machine_data; if store missing, proceed stateless
        try:
            new_md, new_human, diff = patch(payload.machine_data.model_dump(), payload.human_text, payload.validation_report.model_dump(by_alias=True))
        except ValueError as e:
            raise HTTPException(status_code=400, detail={
                "error_code": "ERR_PATCH_VALIDATION_FAILED",
                "human_readable_message": str(e),
                "affected_fields": [],
                "remediation": {"type": "manual", "instruction": "Review patch criteria and re-run"},
            })

        out = {
            "machine_data": new_md,
            "human_text": new_human,
            "diff": diff,
            "version": new_md["version"],
            "machine_data_hash": new_md["machine_data_hash"],
            "status": "patched",
        }

        append_audit("patch", "system", {"old_hash": payload.machine_data.machine_data_hash, "new_hash": new_md["machine_data_hash"], "diff": diff})

        # update store
        store.save(TechniqueRecord(machine_data=new_md, human_text=new_human, status="patched", attempts_history=[payload.validation_report.model_dump(by_alias=True)]))

        return JSONResponse(out)


@app.post("/finalizeTechnique")
def finalize_technique(payload: FinalizeInput):
    with time_block("finalize_ms"):
        attempts = len(payload.attempts_history)
        # Determine pass by last validation in attempts_history if available
        latest_score = 0.0
        latest_pass = False
        if attempts > 0:
            last = payload.attempts_history[-1]
            latest_score = last.get("score", 0.0)
            latest_pass = bool(last.get("pass", False))

        max_iterations = 3
        if attempts >= max_iterations and not latest_pass:
            packet = {
                "final_state": "manual_review",
                "attempts": attempts,
                "total_time_ms": 0,
                "total_tokens_estimated": 0,
                "ingestion_ready": False,
                "recommended_action": "manual_review",
                "error": {
                    "error_code": "ERR_MAX_ITERATIONS_REACHED",
                    "human_readable_message": "Maximum iterations reached without pass",
                    "affected_fields": [],
                    "remediation": {"type": "manual", "instruction": "Escalate to human curator"},
                },
            }
            append_audit("finalize", "system", packet)
            return JSONResponse(packet)

        final_state = "final_validated" if latest_pass and latest_score >= 95.0 else "manual_review"
        ingestion_ready = final_state == "final_validated"
        out = {
            "final_state": final_state,
            "attempts": attempts,
            "total_time_ms": 0,
            "total_tokens_estimated": 0,
            "ingestion_ready": ingestion_ready,
            "recommended_action": "ingest" if ingestion_ready else "manual_review",
        }
        append_audit("finalize", "system", out)
        return JSONResponse(out)


@app.post("/ingestTechnique")
def ingest(payload: TechniqueEnvelope):
    # Ingestion must not modify machine_data
    # Simulate mapping to lore DB by verifying hash is consistent
    recomputed = sha256_hex_lower(canonical_json(payload.machine_data.model_dump()))
    if recomputed != payload.machine_data.machine_data_hash:
        raise HTTPException(status_code=400, detail={
            "error_code": "ERR_MAPPING_CONFLICT",
            "human_readable_message": "machine_data hash mismatch during ingestion",
            "affected_fields": ["machine_data_hash"],
            "remediation": {"type": "manual", "instruction": "Recompute hash before ingestion"},
        })
    ingested_at = datetime.now(timezone.utc).isoformat()
    out = {
        "ingestion_log_id": payload.machine_data.machine_data_hash,
        "ingested_at": ingested_at,
        "lore_entry_id": payload.machine_data.name_id,
    }
    append_audit("ingest", "system", out)
    return JSONResponse(out)
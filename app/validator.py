from __future__ import annotations
from typing import Any, Dict, List
from .schemas import MachineData, ValidationReport, ValidationCriterion
from .constants import (
    CORE_CONCEPT_TEXT,
    HUMAN_TEXT_TEMPLATE,
)
from .hash_util import canonical_json, sha256_hex_lower
import json

VALIDATOR_VERSION = "v1.0"


def build_human_text(md: MachineData) -> str:
    special = md.special_properties if md.special_properties else []
    st = "None" if len(special) == 0 else ",".join(special)
    return HUMAN_TEXT_TEMPLATE.format(
        name=md.name,
        type=md.type,
        core_concept_text=md.core_concept_text,
        description=md.description,
        power_output_pct=format(md.power_output_pct, ".1f").rstrip("0").rstrip(".") if md.power_output_pct % 1 == 0 else f"{md.power_output_pct}",
        power_output_stat=md.power_output_stat,
        effect=md.effect,
        manifestation=",".join(md.manifestation_tags),
        qi_cost_percent=format(md.qi_cost_percent, ".1f").rstrip("0").rstrip(".") if md.qi_cost_percent % 1 == 0 else f"{md.qi_cost_percent}",
        activation_time_value=format(md.activation_time_value, ".1f").rstrip("0").rstrip(".") if md.activation_time_value % 1 == 0 else f"{md.activation_time_value}",
        activation_time_unit=md.activation_time_unit,
        intended_application=",".join(md.intended_application),
        special_properties=st,
        drawbacks=",".join(md.drawbacks),
    )


def validate(machine_data: Dict[str, Any], human_text: str) -> ValidationReport:
    criteria: List[ValidationCriterion] = []

    # 1. Schema validation via Pydantic
    try:
        md = MachineData(**machine_data)
        schema_ok = True
        schema_err = None
    except Exception as e:
        schema_ok = False
        schema_err = str(e)

    criteria.append(
        ValidationCriterion(
            id="ERR_SCHEMA_VIOLATION" if not schema_ok else "SCHEMA_OK",
            description="Pydantic schema validation",
            expected="valid per schema",
            actual=schema_err if not schema_ok else "ok",
            **{"pass": schema_ok},
            severity="error" if not schema_ok else "warning",
            remediation={
                "type": "manual" if not schema_ok else "manual",
                "patch_snippet": {},
                "explanation": schema_err or "No action",
            },
        )
    )

    if not schema_ok:
        total_errors = 1
        total_warnings = 0
        return ValidationReport(
            **{"pass": False},
            score=0.0,
            criteria=criteria,
            summary="Schema invalid",
            total_errors=total_errors,
            total_warnings=total_warnings,
            validator_version=VALIDATOR_VERSION,
        )

    # 2. Core concept exact match sanity (redundant with schema but explicit)
    cc_ok = md.core_concept_text == CORE_CONCEPT_TEXT
    criteria.append(
        ValidationCriterion(
            id="ERR_CORECONCEPT_MISMATCH" if not cc_ok else "CORECONCEPT_OK",
            description="Core concept text must match canonical literal",
            expected=CORE_CONCEPT_TEXT,
            actual=md.core_concept_text,
            **{"pass": cc_ok},
            severity="error" if not cc_ok else "warning",
            remediation={
                "type": "auto_patch" if not cc_ok else "manual",
                "patch_snippet": {"core_concept_text": CORE_CONCEPT_TEXT} if not cc_ok else {},
                "explanation": "Replace with canonical core concept text",
            },
        )
    )

    # 3. Machine hash verification
    canonical = canonical_json(machine_data)
    recomputed = sha256_hex_lower(canonical)
    hash_ok = md.machine_data_hash == recomputed
    criteria.append(
        ValidationCriterion(
            id="ERR_HASH_MISMATCH" if not hash_ok else "HASH_OK",
            description="machine_data_hash must be sha256 of canonical JSON (keys sorted)",
            expected=recomputed,
            actual=md.machine_data_hash,
            **{"pass": hash_ok},
            severity="error" if not hash_ok else "warning",
            remediation={
                "type": "auto_patch" if not hash_ok else "manual",
                "patch_snippet": {"machine_data_hash": recomputed} if not hash_ok else {},
                "explanation": "Recompute hash over canonical JSON (excluding machine_data_hash)",
            },
        )
    )

    # 4. Human text exact template check
    expected_human = build_human_text(md)
    human_ok = human_text == expected_human
    criteria.append(
        ValidationCriterion(
            id="ERR_HUMAN_TEXT_FORMAT" if not human_ok else "HUMAN_TEXT_OK",
            description="Human text must match exact template",
            expected=expected_human,
            actual=human_text,
            **{"pass": human_ok},
            severity="error" if not human_ok else "warning",
            remediation={
                "type": "manual",
                "patch_snippet": {"human_text": expected_human},
                "explanation": "Rebuild human_text from machine_data template",
            },
        )
    )

    # 5. Deterministic numeric bounds (already enforced) plus effect length <= 140
    effect_ok = len(md.effect) <= 140 and len(md.effect) > 0
    criteria.append(
        ValidationCriterion(
            id="ERR_SCHEMA_VIOLATION" if not effect_ok else "EFFECT_OK",
            description="Effect must be non-empty and <= 140 chars",
            expected="1..140 chars",
            actual=len(md.effect),
            **{"pass": effect_ok},
            severity="error" if not effect_ok else "warning",
            remediation={
                "type": "manual",
                "patch_snippet": {},
                "explanation": "Shorten or provide effect",
            },
        )
    )

    # 6. Manifestation tags length <= 6 and items strings
    mani_ok = isinstance(md.manifestation_tags, list) and len(md.manifestation_tags) <= 6
    criteria.append(
        ValidationCriterion(
            id="ERR_MANIFESTATION_MISMATCH" if not mani_ok else "MANIFESTATION_OK",
            description="Manifestation tags must be array of strings, max 6",
            expected="<=6 strings",
            actual=json.dumps(md.manifestation_tags),
            **{"pass": mani_ok},
            severity="error" if not mani_ok else "warning",
            remediation={
                "type": "manual",
                "patch_snippet": {},
                "explanation": "Fix manifestation tags",
            },
        )
    )

    # 7. Description recommended band 50-200 -> if outside, warning to trigger semantic audit
    style_ok = 50 <= len(md.description) <= 200
    criteria.append(
        ValidationCriterion(
            id="STYLE_LENGTH_RECOMMENDATION" if not style_ok else "STYLE_OK",
            description="Description recommended length 50-200 chars",
            expected="50-200",
            actual=len(md.description),
            **{"pass": style_ok},
            severity="warning",
            remediation={
                "type": "manual",
                "patch_snippet": {},
                "explanation": "Consider concise description",
            },
        )
    )

    total_errors = sum(1 for c in criteria if (not c.pass_) and c.severity == "error")
    total_warnings = sum(1 for c in criteria if (not c.pass_) and c.severity == "warning")

    # Scoring heuristic: start 100, minus 20 per error, minus 2 per warning
    score = max(0.0, 100.0 - total_errors * 20.0 - total_warnings * 2.0)
    passed = total_errors == 0 and score >= 95.0

    return ValidationReport(
        **{"pass": passed},
        score=score,
        criteria=criteria,
        summary="Pass" if passed else "Failing criteria present",
        total_errors=total_errors,
        total_warnings=total_warnings,
        validator_version=VALIDATOR_VERSION,
    )
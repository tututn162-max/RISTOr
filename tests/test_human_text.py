from app.validator import build_human_text, validate
from app.schemas import MachineData
from app.constants import CORE_CONCEPT_ID, CORE_CONCEPT_TEXT


def base_md():
    return {
        "name": "Iron Bastion",
        "name_id": "iron-bastion",
        "type": "Defensive",
        "core_concept_id": CORE_CONCEPT_ID,
        "core_concept_text": CORE_CONCEPT_TEXT,
        "description": "X" * 60,
        "power_output_pct": 120.0,
        "power_output_stat": "DU",
        "effect": "Boosts defense",
        "manifestation_tags": ["aura-shimmer"],
        "qi_cost_percent": 10.0,
        "activation_time_value": 1.0,
        "activation_time_unit": "seconds",
        "intended_application": ["training"],
        "special_properties": [],
        "drawbacks": ["fatigue"],
        "human_text": "",
        "machine_data_hash": "",
        "seed": "s",
        "request_id": "r",
        "version": 1,
        "parent_hash": None,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
    }


def test_human_text_exact_template_and_hash():
    md = base_md()
    # build human text requires MachineData with hash placeholder
    human = build_human_text(MachineData(**{**md, "human_text": "", "machine_data_hash": "x" * 64}))
    md["human_text"] = human

    from app.hash_util import canonical_json, sha256_hex_lower
    md["machine_data_hash"] = sha256_hex_lower(canonical_json(md))

    v = validate(md, human)
    assert v.pass_ is True
    assert v.score >= 95.0
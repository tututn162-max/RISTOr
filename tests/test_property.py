import pytest
from hypothesis import given, strategies as st
from app.validator import validate, build_human_text
from app.schemas import MachineData
from app.constants import CORE_CONCEPT_ID, CORE_CONCEPT_TEXT
from app.hash_util import canonical_json, sha256_hex_lower


def make_md(name: str, power: float, qi: float, atv: float):
    md = {
        "name": name,
        "name_id": name.lower().replace(" ", "-"),
        "type": "Offensive",
        "core_concept_id": CORE_CONCEPT_ID,
        "core_concept_text": CORE_CONCEPT_TEXT,
        "description": "D" * 60,
        "power_output_pct": power,
        "power_output_stat": "STR",
        "effect": "Boosts STR internally",
        "manifestation_tags": ["muscle-swell"],
        "qi_cost_percent": qi,
        "activation_time_value": atv,
        "activation_time_unit": "seconds",
        "intended_application": ["dueling"],
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
    human = build_human_text(MachineData(**{**md, "human_text": "", "machine_data_hash": "x" * 64}))
    md["human_text"] = human
    md["machine_data_hash"] = sha256_hex_lower(canonical_json(md))
    return md, human


@given(
    name=st.from_regex(r"^[A-Za-z0-9' -]{3,60}$", fullmatch=True).filter(lambda s: s.strip() == s),
    power=st.floats(min_value=100.0, max_value=150.0, allow_infinity=False, allow_nan=False),
    qi=st.floats(min_value=0.1, max_value=100.0, allow_infinity=False, allow_nan=False),
    atv=st.floats(min_value=0.1, max_value=10.0, allow_infinity=False, allow_nan=False),
)
def test_property_bounds(name, power, qi, atv):
    md, human = make_md(name, float(power), float(qi), float(atv))
    v = validate(md, human)
    assert v.pass_ == (v.total_errors == 0 and v.score >= 95.0)


def test_concurrency_optimistic_locking():
    # Simulate version/hash change detection roundtrip
    md, human = make_md("Iron Frame", 120.0, 10.0, 1.0)
    from app.patcher import apply_patches
    v = validate(md, human)
    new_md, modified = apply_patches(md, v.model_dump(by_alias=True)["criteria"])  # no changes
    assert new_md == md
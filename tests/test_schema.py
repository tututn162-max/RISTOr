import re
from app.schemas import MachineData
from app.constants import CORE_CONCEPT_ID, CORE_CONCEPT_TEXT


def test_name_regex_valid():
    md = MachineData(
        name="Iron Bastion",
        name_id="iron-bastion",
        type="Defensive",
        core_concept_id=CORE_CONCEPT_ID,
        core_concept_text=CORE_CONCEPT_TEXT,
        description="X" * 60,
        power_output_pct=120.0,
        power_output_stat="DU",
        effect="Boosts defense",
        manifestation_tags=["aura-shimmer"],
        qi_cost_percent=10.0,
        activation_time_value=1.0,
        activation_time_unit="seconds",
        intended_application=["training"],
        special_properties=[],
        drawbacks=["causes fatigue"],
        human_text="placeholder",
        machine_data_hash="0" * 64,
        seed="s",
        request_id="r",
        version=1,
        parent_hash=None,
        created_at="2025-01-01T00:00:00+00:00",
        updated_at="2025-01-01T00:00:00+00:00",
    )
    assert md.name == "Iron Bastion"


def test_name_regex_invalid():
    import pytest
    with pytest.raises(Exception):
        MachineData(
            name=" Bad",
            name_id="bad",
            type="Defensive",
            core_concept_id=CORE_CONCEPT_ID,
            core_concept_text=CORE_CONCEPT_TEXT,
            description="X" * 60,
            power_output_pct=120.0,
            power_output_stat="DU",
            effect="Boosts defense",
            manifestation_tags=["aura-shimmer"],
            qi_cost_percent=10.0,
            activation_time_value=1.0,
            activation_time_unit="seconds",
            intended_application=["training"],
            special_properties=[],
            drawbacks=["fatigue"],
            human_text="placeholder",
            machine_data_hash="0" * 64,
            seed="s",
            request_id="r",
            version=1,
            parent_hash=None,
            created_at="2025-01-01T00:00:00+00:00",
            updated_at="2025-01-01T00:00:00+00:00",
        )
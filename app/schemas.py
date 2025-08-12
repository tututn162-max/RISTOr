from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re
from datetime import datetime
from .constants import TECHNIQUE_TYPES, POWER_OUTPUT_STATS, ACTIVATION_TIME_UNITS, CORE_CONCEPT_ID, CORE_CONCEPT_TEXT

NAME_REGEX = re.compile(r"^[A-Za-z0-9'\- ]{3,60}$")

class MachineData(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False)

    name: str = Field(...)
    name_id: str = Field(...)
    type: str = Field(...)
    core_concept_id: str = Field(...)
    core_concept_text: str = Field(...)
    description: str = Field(..., min_length=50, max_length=500)
    power_output_pct: float = Field(..., ge=100.0, le=150.0)
    power_output_stat: str = Field(...)
    effect: str = Field(..., max_length=140)
    manifestation_tags: List[str] = Field(..., min_length=0, max_length=6)
    qi_cost_percent: float = Field(..., gt=0.0, le=100.0)
    activation_time_value: float = Field(..., ge=0.1)
    activation_time_unit: str = Field(...)
    intended_application: List[str] = Field(..., min_length=0, max_length=6)
    special_properties: Optional[List[str]] = Field(default=None)
    drawbacks: List[str] = Field(..., min_length=1)
    human_text: str = Field(...)
    machine_data_hash: str = Field(...)
    seed: str = Field(...)
    request_id: str = Field(...)
    version: int = Field(..., ge=1)
    parent_hash: Optional[str] = Field(default=None)
    created_at: str = Field(...)
    updated_at: str = Field(...)

    @field_validator("name")
    @classmethod
    def validate_name_regex(cls, v: str) -> str:
        if not NAME_REGEX.match(v):
            raise ValueError("ERR_NAME_REGEX_VIOLATION")
        if v != v.strip():
            raise ValueError("ERR_NAME_REGEX_VIOLATION")
        return v

    @field_validator("type")
    @classmethod
    def validate_type_enum(cls, v: str) -> str:
        if v not in TECHNIQUE_TYPES:
            raise ValueError("ERR_INVALID_ENUM")
        return v

    @field_validator("power_output_stat")
    @classmethod
    def validate_stat_enum(cls, v: str) -> str:
        if v not in POWER_OUTPUT_STATS:
            raise ValueError("ERR_INVALID_ENUM")
        return v

    @field_validator("activation_time_unit")
    @classmethod
    def validate_time_unit_enum(cls, v: str) -> str:
        if v not in ACTIVATION_TIME_UNITS:
            raise ValueError("ERR_INVALID_ENUM")
        return v

    @field_validator("core_concept_id")
    @classmethod
    def validate_core_id(cls, v: str) -> str:
        if v != CORE_CONCEPT_ID:
            raise ValueError("ERR_CORECONCEPT_MISMATCH")
        return v

    @field_validator("core_concept_text")
    @classmethod
    def validate_core_text(cls, v: str) -> str:
        if v != CORE_CONCEPT_TEXT:
            raise ValueError("ERR_CORECONCEPT_MISMATCH")
        return v

    @field_validator("effect")
    @classmethod
    def validate_effect_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ERR_SCHEMA_VIOLATION")
        return v

class GenerateRequest(BaseModel):
    seed: str
    request_id: str
    name_uniqueness_required: bool = True
    allowed_tags_list_id: Optional[str] = None
    example_meta_instruction: Optional[str] = None

class TechniqueEnvelope(BaseModel):
    machine_data: MachineData
    human_text: str

class ValidationCriterion(BaseModel):
    id: str
    description: str
    expected: str | float | int | None
    actual: str | float | int | None
    pass_: bool = Field(alias="pass")
    severity: Literal["error", "warning"]
    remediation: dict

class ValidationReport(BaseModel):
    pass_: bool = Field(alias="pass")
    score: float
    criteria: list[ValidationCriterion]
    summary: str
    total_errors: int
    total_warnings: int
    validator_version: str

class ValidateInput(BaseModel):
    machine_data: MachineData
    human_text: str

class PatchInput(BaseModel):
    machine_data: MachineData
    human_text: str
    validation_report: ValidationReport

class PatchOutput(BaseModel):
    machine_data: MachineData
    human_text: str
    diff: dict
    version: int
    machine_data_hash: str
    status: str

class FinalizeInput(BaseModel):
    machine_data: MachineData
    human_text: str
    attempts_history: list

class FinalizeOutput(BaseModel):
    final_state: Literal["final_validated", "manual_review", "quarantined"]
    attempts: int
    total_time_ms: int
    total_tokens_estimated: int
    ingestion_ready: bool
    recommended_action: str
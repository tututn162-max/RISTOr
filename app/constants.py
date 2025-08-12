CORE_CONCEPT_TEXT = (
    "Core Concept: At this stage, a cultivator cannot manifest Qi externally as a separate construct. All techniques are strictly internal, focused on enhancing their own physical body. Their body is the sole vessel and expression of their power."
)

CORE_CONCEPT_ID = "CC-V1"

TECHNIQUE_TYPES = {"Offensive", "Defensive", "Utility", "Movement"}
POWER_OUTPUT_STATS = {"STR", "AG", "STA", "DU", "VIT"}
ACTIVATION_TIME_UNITS = {"seconds", "rounds", "actions"}

WORKFLOW_STATUSES = {
    "generated",
    "validated",
    "patched",
    "final_validated",
    "ingested",
    "manual_review",
    "quarantined",
}

ERROR_CODES = [
    "ERR_SCHEMA_VIOLATION",
    "ERR_CORECONCEPT_MISMATCH",
    "ERR_MISSING_FIELD",
    "ERR_INVALID_ENUM",
    "ERR_POWER_RANGE_OUT_OF_BOUNDS",
    "ERR_QI_COST_INVALID",
    "ERR_HUMAN_TEXT_FORMAT",
    "ERR_HASH_MISMATCH",
    "ERR_NAME_REGEX_VIOLATION",
    "ERR_MANIFESTATION_MISMATCH",
    "ERR_PATCH_VALIDATION_FAILED",
    "ERR_MAX_ITERATIONS_REACHED",
    "ERR_MAPPING_CONFLICT",
    "ERR_LLM_HALLUCINATION",
    "ERR_CONTRADICTORY_REQUIREMENTS",
    "ERR_CONFLICT",
]

HUMAN_TEXT_TEMPLATE = (
    "Technique - {name}\n"
    "Type: {type}\n"
    "Core Concept: {core_concept_text}\n"
    "Description: {description}\n"
    "Power Output: [+{power_output_pct}% Increase in {power_output_stat}]\n"
    "Effect: {effect}\n"
    "Manifestation: {manifestation}\n"
    "Qi Cost: [{qi_cost_percent}% of Total Capacity]\n"
    "Activation Time: [{activation_time_value} {activation_time_unit}]\n"
    "Intended Application: {intended_application}\n"
    "Special Properties: {special_properties}\n"
    "Drawbacks: {drawbacks}"
)

META_INSTRUCTION = (
    "META-INSTRUCTION (MANDATORY): The following is an example of the style and format required. DO NOT copy content. Focus on structure and constraints. Base your response only on the provided reference points. If the information is not present, state \"Information not available\". Use only the canonical core concept literal when required. Do not invent facts or mechanics outside the provided machine_data fields. When asked to modify fields, return machine-readable JSON only, no extra commentary."
)

EXAMPLE_METADATA = (
    "EXAMPLE METADATA (REQUIRED): The following is an example of the style and format required. DO NOT copy content. Focus on structure and constraints demonstrated."
)
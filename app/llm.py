import os
import json
from typing import Any, Dict, List
from .constants import META_INSTRUCTION

# Optional Gemini Integration; degrade gracefully if API key missing
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore


def _get_client():  # pragma: no cover - networking excluded in tests
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return None
    genai.configure(api_key=api_key)
    return genai


def semantic_audit_prompt(machine_data: Dict[str, Any], human_text: str, failing_warnings: List[Dict[str, Any]]) -> str:
    payload = {
        "machine_data": machine_data,
        "human_text": human_text,
        "failing_warnings": failing_warnings,
    }
    return (
        META_INSTRUCTION
        + "\n\n"
        + "You are given machine_data and human_text for a technique. Check for semantic mismatches strictly based on the rules. If information is insufficient, reply with \"Information not available\". Output JSON with keys: issues:[{id,description,severity,field,explanation}] and recommended_patches:[{field,old,new}] only.\n\n"
        + json.dumps(payload)
    )


def call_semantic_audit(machine_data: Dict[str, Any], human_text: str, failing_warnings: List[Dict[str, Any]]) -> Dict[str, Any]:  # pragma: no cover
    client = _get_client()
    if client is None:
        return {"issues": [], "recommended_patches": []}
    prompt = semantic_audit_prompt(machine_data, human_text, failing_warnings)
    model = client.GenerativeModel("gemini-2.5-pro")
    resp = model.generate_content(prompt)
    try:
        text = resp.text
        data = json.loads(text)
        return data
    except Exception:
        return {"issues": [], "recommended_patches": []}


def targeted_rewrite_prompt(machine_data: Dict[str, Any], failing_criteria: List[Dict[str, Any]]) -> str:
    payload = {
        "machine_data": machine_data,
        "failing_criteria": failing_criteria,
    }
    return (
        META_INSTRUCTION
        + "\n\n"
        + "You are given the following machine_data JSON and the failing criteria: [<list>]. Apply minimal edits only to the specified fields to satisfy the criteria. Return only the updated JSON fragment with keys and values. Do not change other fields. If you cannot satisfy the criteria without violating another explicit constraint, return {\"error\":\"Cannot produce valid patch\"}.\n\n"
        + json.dumps(payload)
    )


def call_targeted_rewrite(machine_data: Dict[str, Any], failing_criteria: List[Dict[str, Any]]) -> Dict[str, Any]:  # pragma: no cover
    client = _get_client()
    if client is None:
        return {"error": "LLM unavailable"}
    prompt = targeted_rewrite_prompt(machine_data, failing_criteria)
    model = client.GenerativeModel("gemini-2.5-pro")
    resp = model.generate_content(prompt)
    try:
        text = resp.text
        data = json.loads(text)
        return data
    except Exception:
        return {"error": "Invalid LLM response"}
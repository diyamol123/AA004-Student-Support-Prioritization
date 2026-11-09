"""In-memory audit storage for AA004 workflow executions."""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


_AUDIT_RECORDS: dict[str, dict[str, Any]] = {}


def record_workflow(
    workflow_id: str,
    student_case: dict,
    agent_sequence: list[str],
    agent_outputs: list[dict],
    triggered_rules: list[str],
    final_recommendation: dict,
    errors: list[str],
    node_trace: list[str] | None = None,
) -> str:
    """Store a traceable record of one workflow execution."""

    audit_reference = f"AUDIT-{workflow_id}"

    _AUDIT_RECORDS[audit_reference] = {
        "audit_reference": audit_reference,
        "workflow_id": workflow_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_reference": student_case.get("case_id"),
        "agent_sequence": agent_sequence,
        "agent_outputs": deepcopy(agent_outputs),
        "triggered_rules": triggered_rules,
        "final_recommendation": deepcopy(final_recommendation),
        "errors": list(errors),
        "node_trace": list(node_trace or []),
    }

    return audit_reference


def get_audit_record(audit_reference: str) -> dict | None:
    """Retrieve one audit record without exposing mutable stored data."""

    record = _AUDIT_RECORDS.get(audit_reference)
    return deepcopy(record) if record is not None else None


def clear_audit_records() -> None:
    """Clear in-memory audit records, primarily for isolated tests."""

    _AUDIT_RECORDS.clear()

"""Tests for the Case Intake Agent."""

import pytest

from backend.app.agents.case_intake_agent import run_case_intake
from backend.app.models.schemas import StudentCaseInput


def test_complete_case_is_validated():
    case = StudentCaseInput(
        case_id=" CASE-001 ",
        attendance_rate=68,
        missed_submissions=3,
        engagement_status="inactive",
        days_since_last_activity=18,
        unresolved_support_tickets=2,
    )

    validated, output = run_case_intake(case)

    assert validated.case_id == "CASE-001"
    assert validated.missing_fields == []
    assert output.status == "COMPLETED"
    assert output.flag == "VALID"


def test_missing_evidence_is_identified():
    case = StudentCaseInput(case_id="CASE-002")

    validated, output = run_case_intake(case)

    assert "attendance_rate" in validated.missing_fields
    assert "missed_submissions" in validated.missing_fields
    assert "engagement_status" in validated.missing_fields
    assert "unresolved_support_tickets" in validated.missing_fields
    assert output.status == "NEEDS_INFORMATION"
    assert output.flag == "INCOMPLETE"


def test_activity_indicators_are_normalized():
    case = StudentCaseInput(
        case_id="CASE-003",
        recent_activity_indicators=[
            "  attended tutorial  ",
            "ATTENDED TUTORIAL",
            "",
            "submitted assignment",
        ],
    )

    validated, _ = run_case_intake(case)

    assert validated.recent_activity_indicators == [
        "attended tutorial",
        "submitted assignment",
    ]


def test_blank_case_id_is_rejected():
    case = StudentCaseInput(case_id="   ")

    with pytest.raises(ValueError, match="Case ID cannot be blank"):
        run_case_intake(case)

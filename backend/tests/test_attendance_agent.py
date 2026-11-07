"""Tests for the Attendance Agent."""

import pytest

from backend.app.agents.attendance_agent import evaluate_attendance
from backend.app.models.schemas import ValidatedCase


@pytest.mark.parametrize(
    ("attendance", "expected_flag", "expected_score"),
    [
        (60, "HIGH", 30),
        (74.9, "HIGH", 30),
        (75, "MODERATE", 15),
        (84.9, "MODERATE", 15),
        (85, "NONE", 0),
        (100, "NONE", 0),
    ],
)
def test_attendance_thresholds(attendance, expected_flag, expected_score):
    case = ValidatedCase(
        case_id="CASE-ATTENDANCE",
        attendance_rate=attendance,
    )

    output = evaluate_attendance(case)

    assert output.status == "COMPLETED"
    assert output.flag == expected_flag
    assert output.score == expected_score


def test_missing_attendance_is_not_treated_as_zero():
    case = ValidatedCase(case_id="CASE-MISSING")

    output = evaluate_attendance(case)

    assert output.status == "NEEDS_INFORMATION"
    assert output.flag == "UNAVAILABLE"
    assert output.score == 0
    assert output.output_data["attendance_rate"] is None


def test_attendance_evidence_is_traceable():
    case = ValidatedCase(
        case_id="CASE-EVIDENCE",
        attendance_rate=70,
    )

    output = evaluate_attendance(case)

    assert len(output.evidence) == 2
    assert output.evidence[0].value == 70
    assert output.output_data["threshold_type"] == "demo_assumption"

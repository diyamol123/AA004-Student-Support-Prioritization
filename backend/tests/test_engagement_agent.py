"""Tests for the Engagement Agent."""

import pytest

from backend.app.agents.engagement_agent import evaluate_engagement
from backend.app.models.schemas import ValidatedCase


@pytest.mark.parametrize(
    ("days", "expected_flag", "expected_score"),
    [
        (30, "HIGH", 20),
        (14, "HIGH", 20),
        (13, "MODERATE", 10),
        (7, "MODERATE", 10),
        (6, "NONE", 0),
        (0, "NONE", 0),
    ],
)
def test_engagement_thresholds(days, expected_flag, expected_score):
    case = ValidatedCase(
        case_id="CASE-ENGAGEMENT",
        days_since_last_activity=days,
    )

    output = evaluate_engagement(case)

    assert output.status == "COMPLETED"
    assert output.flag == expected_flag
    assert output.score == expected_score


def test_missing_inactivity_duration_is_unavailable():
    case = ValidatedCase(
        case_id="CASE-MISSING",
        engagement_status="inactive",
    )

    output = evaluate_engagement(case)

    assert output.status == "NEEDS_INFORMATION"
    assert output.flag == "UNAVAILABLE"
    assert output.score == 0
    assert output.output_data["days_since_last_activity"] is None


def test_engagement_evidence_is_traceable():
    case = ValidatedCase(
        case_id="CASE-EVIDENCE",
        days_since_last_activity=15,
        engagement_status="inactive",
    )

    output = evaluate_engagement(case)

    assert output.flag == "HIGH"
    assert output.score == 20
    assert len(output.evidence) == 3
    assert output.evidence[0].value == 15
    assert output.evidence[1].value == "inactive"
    assert output.output_data["threshold_type"] == "demo_assumption"

"""Tests for the Support Load Agent."""

import pytest

from backend.app.agents.support_load_agent import evaluate_support_load
from backend.app.models.schemas import ValidatedCase


@pytest.mark.parametrize(
    ("missed", "tickets", "expected_score", "expected_flag"),
    [
        (0, 0, 0, "NONE"),
        (1, 0, 15, "MODERATE"),
        (2, 0, 30, "HIGH"),
        (0, 1, 10, "MODERATE"),
        (0, 2, 20, "HIGH"),
        (2, 2, 50, "HIGH"),
        (1, 1, 25, "MODERATE"),
    ],
)
def test_support_load_scores(missed, tickets, expected_score, expected_flag):
    case = ValidatedCase(
        case_id="CASE-SUPPORT",
        missed_submissions=missed,
        unresolved_support_tickets=tickets,
    )

    output = evaluate_support_load(case)

    assert output.status == "COMPLETED"
    assert output.score == expected_score
    assert output.flag == expected_flag


def test_missing_evidence_is_reported():
    case = ValidatedCase(case_id="CASE-MISSING")

    output = evaluate_support_load(case)

    assert output.status == "NEEDS_INFORMATION"
    assert output.flag == "UNAVAILABLE"
    assert output.score == 0
    assert set(output.output_data["missing_fields"]) == {
        "missed_submissions",
        "unresolved_support_tickets",
    }


def test_partial_evidence_is_still_evaluated():
    case = ValidatedCase(
        case_id="CASE-PARTIAL",
        missed_submissions=2,
    )

    output = evaluate_support_load(case)

    assert output.status == "NEEDS_INFORMATION"
    assert output.score == 30
    assert output.output_data["missed_submissions_flag"] == "HIGH"
    assert output.output_data["unresolved_tickets_flag"] == "UNAVAILABLE"


def test_support_evidence_is_traceable():
    case = ValidatedCase(
        case_id="CASE-EVIDENCE",
        missed_submissions=2,
        unresolved_support_tickets=1,
    )

    output = evaluate_support_load(case)

    assert len(output.evidence) == 3
    assert output.evidence[0].value == 2
    assert output.evidence[1].value == 1
    assert output.output_data["threshold_type"] == "demo_assumption"

"""Tests for the Student Support Decision Agent."""

from backend.app.agents.student_support_decision_agent import make_decision
from backend.app.models.schemas import (
    AgentOutput,
    RecommendationAction,
    ValidatedCase,
)


def make_output(name, flag="NONE", score=0, status="COMPLETED",
                missed_flag=None, tickets_flag=None):
    return AgentOutput(
        agent_name=name,
        status=status,
        summary=f"{name} test output",
        flag=flag,
        score=score,
        output_data={
            "missed_submissions_flag": missed_flag,
            "unresolved_tickets_flag": tickets_flag,
        },
    )


def decide(case, attendance, engagement, support, inconsistencies=None):
    return make_decision(
        case,
        attendance,
        engagement,
        support,
        inconsistencies,
    )


def test_low_attendance_and_multiple_missed_submissions_get_priority():
    case = ValidatedCase(
        case_id="CASE-PRIORITY",
        attendance_rate=70,
        missed_submissions=3,
    )

    result = decide(
        case,
        make_output("Attendance Agent", "HIGH", 30),
        make_output("Engagement Agent"),
        make_output(
            "Support Load Agent",
            "HIGH",
            30,
            missed_flag="HIGH",
            tickets_flag="NONE",
        ),
    )

    assert result.action == RecommendationAction.PRIORITY_OUTREACH
    assert result.triggered_rules == [
        "RULE-03-LOW-ATTENDANCE-AND-MISSED-WORK"
    ]
    assert result.priority_score == 60


def test_incomplete_evidence_requests_more_information():
    case = ValidatedCase(case_id="CASE-INCOMPLETE")

    result = decide(
        case,
        make_output("Attendance Agent", status="NEEDS_INFORMATION"),
        make_output("Engagement Agent"),
        make_output("Support Load Agent"),
    )

    assert result.action == RecommendationAction.REQUEST_MORE_INFO
    assert result.triggered_rules == ["RULE-01-INCOMPLETE-EVIDENCE"]


def test_explicit_inconsistency_requires_tutor_review():
    case = ValidatedCase(
        case_id="CASE-CONFLICT",
        attendance_rate=90,
        missed_submissions=0,
    )

    result = decide(
        case,
        make_output("Attendance Agent"),
        make_output("Engagement Agent"),
        make_output("Support Load Agent"),
        inconsistencies=["Two supplied records disagree about attendance."],
    )

    assert result.action == RecommendationAction.TUTOR_REVIEW
    assert result.triggered_rules == ["RULE-02-INCONSISTENT-EVIDENCE"]


def test_multiple_moderate_concerns_require_tutor_review():
    case = ValidatedCase(
        case_id="CASE-MULTIPLE",
        attendance_rate=80,
        missed_submissions=1,
    )

    result = decide(
        case,
        make_output("Attendance Agent", "MODERATE", 15),
        make_output("Engagement Agent"),
        make_output(
            "Support Load Agent",
            "MODERATE",
            15,
            missed_flag="MODERATE",
            tickets_flag="NONE",
        ),
    )

    assert result.action == RecommendationAction.TUTOR_REVIEW
    assert result.triggered_rules == [
        "RULE-04-MULTIPLE-OR-HIGH-CONCERNS"
    ]


def test_single_mild_concern_gets_normal_followup():
    case = ValidatedCase(
        case_id="CASE-MILD",
        attendance_rate=80,
        missed_submissions=0,
    )

    result = decide(
        case,
        make_output("Attendance Agent", "MODERATE", 15),
        make_output("Engagement Agent"),
        make_output(
            "Support Load Agent",
            missed_flag="NONE",
            tickets_flag="NONE",
        ),
    )

    assert result.action == RecommendationAction.NORMAL_FOLLOWUP
    assert result.triggered_rules == ["RULE-05-NORMAL-FOLLOWUP"]


def test_no_concerns_get_normal_followup():
    case = ValidatedCase(
        case_id="CASE-NORMAL",
        attendance_rate=95,
        missed_submissions=0,
    )

    result = decide(
        case,
        make_output("Attendance Agent"),
        make_output("Engagement Agent"),
        make_output(
            "Support Load Agent",
            missed_flag="NONE",
            tickets_flag="NONE",
        ),
    )

    assert result.action == RecommendationAction.NORMAL_FOLLOWUP
    assert result.priority_score == 0


def test_high_score_alone_does_not_trigger_priority_outreach():
    case = ValidatedCase(
        case_id="CASE-HIGH-SCORE",
        attendance_rate=90,
        missed_submissions=0,
    )

    result = decide(
        case,
        make_output("Attendance Agent"),
        make_output("Engagement Agent", "HIGH", 20),
        make_output(
            "Support Load Agent",
            "HIGH",
            50,
            missed_flag="NONE",
            tickets_flag="HIGH",
        ),
    )

    assert result.action == RecommendationAction.TUTOR_REVIEW
    assert result.action != RecommendationAction.PRIORITY_OUTREACH


def test_priority_score_is_capped_at_100():
    case = ValidatedCase(
        case_id="CASE-CAPPED",
        attendance_rate=70,
        missed_submissions=3,
    )

    result = decide(
        case,
        make_output("Attendance Agent", "HIGH", 30),
        make_output("Engagement Agent", "HIGH", 20),
        make_output(
            "Support Load Agent",
            "HIGH",
            50,
            missed_flag="HIGH",
            tickets_flag="HIGH",
        ),
    )

    assert result.priority_score == 100

"""Integration tests for the complete AA004 workflow."""

from backend.app.models.schemas import (
    RecommendationAction,
    StudentCaseInput,
)
from backend.app.services.audit_service import (
    clear_audit_records,
    get_audit_record,
)
from backend.app.services.workflow_service import (
    AGENT_SEQUENCE,
    run_student_support_workflow,
)


def setup_function():
    clear_audit_records()


def test_complete_case_runs_all_five_agents():
    case = StudentCaseInput(
        case_id="CASE-WORKFLOW-001",
        attendance_rate=95,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=2,
        unresolved_support_tickets=0,
    )

    context = run_student_support_workflow(case)

    assert len(context.agent_outputs) == 5
    assert [
        output.agent_name for output in context.agent_outputs
    ] == AGENT_SEQUENCE

    assert context.final_recommendation.action == (
        RecommendationAction.NORMAL_FOLLOWUP
    )
    assert context.audit_reference is not None
    assert len(context.explanation) >= 5


def test_priority_case_produces_priority_outreach():
    case = StudentCaseInput(
        case_id="CASE-WORKFLOW-002",
        attendance_rate=68,
        missed_submissions=3,
        engagement_status="inactive",
        days_since_last_activity=18,
        unresolved_support_tickets=2,
    )

    context = run_student_support_workflow(case)

    assert context.final_recommendation.action == (
        RecommendationAction.PRIORITY_OUTREACH
    )
    assert context.final_recommendation.priority_score == 100
    assert (
        "RULE-03-LOW-ATTENDANCE-AND-MISSED-WORK"
        in context.final_recommendation.triggered_rules
    )


def test_incomplete_case_requests_more_information():
    case = StudentCaseInput(
        case_id="CASE-WORKFLOW-003",
        attendance_rate=None,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=2,
        unresolved_support_tickets=0,
    )

    context = run_student_support_workflow(case)

    assert context.final_recommendation.action == (
        RecommendationAction.REQUEST_MORE_INFO
    )


def test_audit_record_contains_actual_execution_evidence():
    case = StudentCaseInput(
        case_id="CASE-WORKFLOW-004",
        attendance_rate=90,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=1,
        unresolved_support_tickets=0,
    )

    context = run_student_support_workflow(case)
    audit = get_audit_record(context.audit_reference)

    assert audit is not None
    assert audit["workflow_id"] == context.workflow_id
    assert audit["input_reference"] == "CASE-WORKFLOW-004"
    assert audit["agent_sequence"] == AGENT_SEQUENCE
    assert len(audit["agent_outputs"]) == 5
    assert audit["final_recommendation"]["action"] == (
        RecommendationAction.NORMAL_FOLLOWUP.value
    )


def test_each_workflow_gets_a_unique_id():
    case = StudentCaseInput(
        case_id="CASE-UNIQUE",
        attendance_rate=90,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=1,
        unresolved_support_tickets=0,
    )

    first = run_student_support_workflow(case)
    second = run_student_support_workflow(case)

    assert first.workflow_id != second.workflow_id
    assert first.audit_reference != second.audit_reference


def test_conflicting_engagement_evidence_requires_tutor_review():
    case = StudentCaseInput(
        case_id="CASE-WORKFLOW-CONFLICT-001",
        attendance_rate=95,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=18,
        unresolved_support_tickets=0,
    )

    context = run_student_support_workflow(case)

    assert context.final_recommendation.action == (
        RecommendationAction.TUTOR_REVIEW
    )
    assert (
        "RULE-02-INCONSISTENT-EVIDENCE"
        in context.final_recommendation.triggered_rules
    )
    assert any(
        "status is active" in evidence.detail
        for evidence in context.final_recommendation.evidence
    )


def test_decision_references_all_four_upstream_agents():
    case = StudentCaseInput(
        case_id="CASE-WORKFLOW-REFS-001",
        attendance_rate=95,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=2,
        unresolved_support_tickets=0,
    )

    context = run_student_support_workflow(case)

    assert context.final_recommendation.agent_output_refs == [
        "Case Intake Agent",
        "Attendance Agent",
        "Engagement Agent",
        "Support Load Agent",
    ]


def test_langgraph_executes_all_seven_nodes_and_records_trace():
    case = StudentCaseInput(
        case_id="CASE-LANGGRAPH-TRACE-001",
        attendance_rate=95,
        missed_submissions=0,
        engagement_status="active",
        days_since_last_activity=2,
        unresolved_support_tickets=0,
    )

    context = run_student_support_workflow(case)

    expected_trace = [
        "Case Intake Agent",
        "Attendance Agent",
        "Engagement Agent",
        "Support Load Agent",
        "Student Support Decision Agent",
        "Explanation Node",
        "Audit Node",
    ]

    audit = get_audit_record(context.audit_reference)

    assert context.node_trace == expected_trace
    assert audit is not None
    assert audit["node_trace"] == expected_trace
    assert len(context.agent_outputs) == 5
    assert context.final_recommendation.action == (
        RecommendationAction.NORMAL_FOLLOWUP
    )

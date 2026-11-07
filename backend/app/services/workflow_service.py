"""Orchestrates the five AA004 agents using shared workflow context."""

from uuid import uuid4

from backend.app.agents.case_intake_agent import run_case_intake
from backend.app.agents.attendance_agent import evaluate_attendance
from backend.app.agents.engagement_agent import evaluate_engagement
from backend.app.agents.support_load_agent import evaluate_support_load
from backend.app.agents.student_support_decision_agent import make_decision
from backend.app.models.schemas import (
    AgentOutput,
    EvidenceItem,
    StudentCaseInput,
    WorkflowContext,
)
from backend.app.services.audit_service import record_workflow


AGENT_SEQUENCE = [
    "Case Intake Agent",
    "Attendance Agent",
    "Engagement Agent",
    "Support Load Agent",
    "Student Support Decision Agent",
]


def run_student_support_workflow(
    student_case: StudentCaseInput,
) -> WorkflowContext:
    """Execute all five agents and return the completed shared context."""

    workflow_id = str(uuid4())

    context = WorkflowContext(
        workflow_id=workflow_id,
        student_case=student_case,
    )

    # Stage 1: validate and normalize business input.
    validated_case, intake_output = run_case_intake(student_case)

    context.validated_case = validated_case
    context.agent_outputs.append(intake_output)

    # Stage 2: run the three independent evidence evaluation agents.
    attendance_output = evaluate_attendance(validated_case)
    engagement_output = evaluate_engagement(validated_case)
    support_output = evaluate_support_load(validated_case)

    context.attendance_flag = attendance_output.flag
    context.engagement_flag = engagement_output.flag
    context.support_load_flag = support_output.flag

    context.scores = {
        "attendance": attendance_output.score,
        "engagement": engagement_output.score,
        "support_load": support_output.score,
    }

    context.agent_outputs.extend([
        attendance_output,
        engagement_output,
        support_output,
    ])

    # Stage 3: combine the actual agent outputs into a recommendation.
    recommendation = make_decision(
        validated_case=validated_case,
        attendance_output=attendance_output,
        engagement_output=engagement_output,
        support_output=support_output,
        inconsistencies=engagement_output.output_data.get(
            "inconsistencies", []
        ),
        intake_output=intake_output,
    )

    context.final_recommendation = recommendation

    # Represent the fifth agent in the execution trace.
    decision_output = AgentOutput(
        agent_name="Student Support Decision Agent",
        status="COMPLETED",
        summary=(
            f"Recommendation: {recommendation.action.value}; "
            f"priority score: {recommendation.priority_score}."
        ),
        score=recommendation.priority_score,
        flag=recommendation.priority_band,
        evidence=recommendation.evidence,
        output_data={
            "action": recommendation.action.value,
            "priority_band": recommendation.priority_band,
            "reasons": recommendation.reasons,
            "triggered_rules": recommendation.triggered_rules,
        },
    )

    context.agent_outputs.append(decision_output)

    # Stage 4: create an explanation from actual workflow evidence.
    context.explanation = [
        f"{output.agent_name}: {output.summary}"
        for output in context.agent_outputs
    ]
    context.explanation.extend(
        f"Decision rule triggered: {rule}"
        for rule in recommendation.triggered_rules
    )
    context.explanation.extend(recommendation.reasons)

    # Stage 5: record the workflow audit.
    context.audit_reference = record_workflow(
        workflow_id=workflow_id,
        student_case=student_case.model_dump(mode="json"),
        agent_sequence=AGENT_SEQUENCE,
        agent_outputs=[
            output.model_dump(mode="json")
            for output in context.agent_outputs
        ],
        triggered_rules=recommendation.triggered_rules,
        final_recommendation=recommendation.model_dump(mode="json"),
        errors=context.errors,
    )

    return context

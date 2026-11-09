"""Linear LangGraph orchestration for the AA004 support workflow."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from backend.app.agents.case_intake_agent import run_case_intake
from backend.app.agents.attendance_agent import evaluate_attendance
from backend.app.agents.engagement_agent import evaluate_engagement
from backend.app.agents.support_load_agent import evaluate_support_load
from backend.app.agents.student_support_decision_agent import make_decision
from backend.app.models.schemas import AgentOutput, WorkflowContext
from backend.app.services.audit_service import record_workflow


AGENT_SEQUENCE = [
    "Case Intake Agent",
    "Attendance Agent",
    "Engagement Agent",
    "Support Load Agent",
    "Student Support Decision Agent",
]


class StudentSupportGraphState(TypedDict):
    """State passed between nodes during one workflow execution."""

    context: WorkflowContext
    node_trace: list[str]


def _with_trace(
    state: StudentSupportGraphState,
    context: WorkflowContext,
    node_name: str,
) -> dict:
    trace = [*state["node_trace"], node_name]
    updated_context = context.model_copy(update={"node_trace": trace})
    return {
        "context": updated_context,
        "node_trace": trace,
    }


def _get_output(context: WorkflowContext, agent_name: str) -> AgentOutput:
    for output in context.agent_outputs:
        if output.agent_name == agent_name:
            return output
    raise ValueError(f"Missing workflow output: {agent_name}")


def case_intake_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    validated_case, intake_output = run_case_intake(context.student_case)

    updated = context.model_copy(
        update={
            "validated_case": validated_case,
            "agent_outputs": [*context.agent_outputs, intake_output],
        }
    )
    return _with_trace(state, updated, "Case Intake Agent")


def attendance_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    if context.validated_case is None:
        raise ValueError("Case Intake must run before Attendance.")

    output = evaluate_attendance(context.validated_case)
    updated = context.model_copy(
        update={
            "attendance_flag": output.flag,
            "scores": {**context.scores, "attendance": output.score},
            "agent_outputs": [*context.agent_outputs, output],
        }
    )
    return _with_trace(state, updated, "Attendance Agent")


def engagement_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    if context.validated_case is None:
        raise ValueError("Case Intake must run before Engagement.")

    output = evaluate_engagement(context.validated_case)
    updated = context.model_copy(
        update={
            "engagement_flag": output.flag,
            "scores": {**context.scores, "engagement": output.score},
            "agent_outputs": [*context.agent_outputs, output],
        }
    )
    return _with_trace(state, updated, "Engagement Agent")


def support_load_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    if context.validated_case is None:
        raise ValueError("Case Intake must run before Support Load.")

    output = evaluate_support_load(context.validated_case)
    updated = context.model_copy(
        update={
            "support_load_flag": output.flag,
            "scores": {**context.scores, "support_load": output.score},
            "agent_outputs": [*context.agent_outputs, output],
        }
    )
    return _with_trace(state, updated, "Support Load Agent")


def decision_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    if context.validated_case is None:
        raise ValueError("Case Intake must run before the Decision node.")

    intake = _get_output(context, "Case Intake Agent")
    attendance = _get_output(context, "Attendance Agent")
    engagement = _get_output(context, "Engagement Agent")
    support = _get_output(context, "Support Load Agent")

    recommendation = make_decision(
        validated_case=context.validated_case,
        attendance_output=attendance,
        engagement_output=engagement,
        support_output=support,
        inconsistencies=engagement.output_data.get("inconsistencies", []),
        intake_output=intake,
    )

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

    updated = context.model_copy(
        update={
            "final_recommendation": recommendation,
            "agent_outputs": [*context.agent_outputs, decision_output],
        }
    )
    return _with_trace(state, updated, "Student Support Decision Agent")


def explanation_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    recommendation = context.final_recommendation
    if recommendation is None:
        raise ValueError("Decision must run before Explanation.")

    explanation = [
        f"{output.agent_name}: {output.summary}"
        for output in context.agent_outputs
    ]
    explanation.extend(
        f"Decision rule triggered: {rule}"
        for rule in recommendation.triggered_rules
    )
    explanation.extend(recommendation.reasons)

    updated = context.model_copy(update={"explanation": explanation})
    return _with_trace(state, updated, "Explanation Node")


def audit_node(state: StudentSupportGraphState) -> dict:
    context = state["context"]
    recommendation = context.final_recommendation
    if recommendation is None:
        raise ValueError("Decision must run before Audit.")

    traced = _with_trace(state, context, "Audit Node")
    context = traced["context"]

    audit_reference = record_workflow(
        workflow_id=context.workflow_id,
        student_case=context.student_case.model_dump(mode="json"),
        agent_sequence=AGENT_SEQUENCE,
        agent_outputs=[
            output.model_dump(mode="json")
            for output in context.agent_outputs
        ],
        triggered_rules=recommendation.triggered_rules,
        final_recommendation=recommendation.model_dump(mode="json"),
        errors=context.errors,
        node_trace=context.node_trace,
    )

    completed = context.model_copy(
        update={"audit_reference": audit_reference}
    )
    traced["context"] = completed
    return traced


def build_student_support_graph():
    """Build and compile the seven-node linear workflow."""

    builder = StateGraph(StudentSupportGraphState)

    builder.add_node("case_intake", case_intake_node)
    builder.add_node("attendance", attendance_node)
    builder.add_node("engagement", engagement_node)
    builder.add_node("support_load", support_load_node)
    builder.add_node("decision", decision_node)
    builder.add_node("explanation", explanation_node)
    builder.add_node("audit", audit_node)

    builder.add_edge(START, "case_intake")
    builder.add_edge("case_intake", "attendance")
    builder.add_edge("attendance", "engagement")
    builder.add_edge("engagement", "support_load")
    builder.add_edge("support_load", "decision")
    builder.add_edge("decision", "explanation")
    builder.add_edge("explanation", "audit")
    builder.add_edge("audit", END)

    return builder.compile()


student_support_graph = build_student_support_graph()

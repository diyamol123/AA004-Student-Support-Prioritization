"""Runs the AA004 workflow through its compiled LangGraph."""

from uuid import uuid4

from backend.app.graphs.student_support_graph import student_support_graph
from backend.app.models.schemas import StudentCaseInput, WorkflowContext


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
    """Execute the conditional LangGraph workflow and return its completed context."""

    workflow_id = str(uuid4())

    initial_context = WorkflowContext(
        workflow_id=workflow_id,
        student_case=student_case,
    )

    result = student_support_graph.invoke(
        {
            "context": initial_context,
            "node_trace": [],
        }
    )

    return result["context"]

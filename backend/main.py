"""FastAPI entry point for AA004 Student Support Case Prioritization."""

from fastapi import FastAPI, HTTPException

from backend.app.models.schemas import StudentCaseInput
from backend.app.services.audit_service import get_audit_record
from backend.app.services.workflow_service import run_student_support_workflow


app = FastAPI(
    title="AA004 - Student Support Case Prioritization",
    description=(
        "Deterministic, explainable academic support case prioritization MVP."
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "case_id": "AA004",
        "service": "Student Support Case Prioritization",
    }


@app.post("/api/workflows/run")
def run_workflow(student_case: StudentCaseInput):
    """Run all five agents for one student support case."""

    try:
        result = run_student_support_workflow(student_case)
        return result.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Workflow execution failed.",
        ) from exc


@app.get("/api/audit/{audit_reference}")
def get_audit(audit_reference: str):
    """Retrieve the audit record for a completed workflow."""

    record = get_audit_record(audit_reference)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Audit record not found.",
        )

    return record

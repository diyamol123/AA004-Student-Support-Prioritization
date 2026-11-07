"""Case Intake Agent: validates and normalizes student support cases."""

from backend.app.models.schemas import (
    AgentOutput,
    EvidenceItem,
    StudentCaseInput,
    ValidatedCase,
)


REQUIRED_EVIDENCE_FIELDS = (
    "attendance_rate",
    "missed_submissions",
    "engagement_status",
    "unresolved_support_tickets",
)


def run_case_intake(
    student_case: StudentCaseInput,
) -> tuple[ValidatedCase, AgentOutput]:
    """Normalize one case and identify evidence that has not been supplied."""

    case_id = student_case.case_id.strip()
    if not case_id:
        raise ValueError("Case ID cannot be blank.")

    indicators = []
    seen = set()

    for indicator in student_case.recent_activity_indicators:
        normalized = indicator.strip()
        key = normalized.casefold()

        if normalized and key not in seen:
            indicators.append(normalized)
            seen.add(key)

    missing_fields = [
        field
        for field in REQUIRED_EVIDENCE_FIELDS
        if getattr(student_case, field) is None
    ]

    validated_case = ValidatedCase(
        case_id=case_id,
        attendance_rate=student_case.attendance_rate,
        missed_submissions=student_case.missed_submissions,
        engagement_status=student_case.engagement_status,
        days_since_last_activity=student_case.days_since_last_activity,
        unresolved_support_tickets=student_case.unresolved_support_tickets,
        recent_activity_indicators=indicators,
        missing_fields=missing_fields,
    )

    evidence = [
        EvidenceItem(
            source="student_case",
            detail=f"{field} was supplied",
            value=str(getattr(validated_case, field)),
        )
        for field in REQUIRED_EVIDENCE_FIELDS
        if getattr(validated_case, field) is not None
    ]

    if missing_fields:
        status = "NEEDS_INFORMATION"
        summary = (
            "Case normalized. Some required support evidence is missing."
        )
    else:
        status = "COMPLETED"
        summary = "Case validated and normalized successfully."

    output = AgentOutput(
        agent_name="Case Intake Agent",
        status=status,
        summary=summary,
        score=0,
        flag="INCOMPLETE" if missing_fields else "VALID",
        evidence=evidence,
        output_data={
            "case_id": case_id,
            "missing_fields": missing_fields,
            "normalized_indicator_count": len(indicators),
        },
    )

    return validated_case, output

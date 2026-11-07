"""Attendance Agent: evaluates attendance against configured demo thresholds."""

from backend.app.models.schemas import (
    AgentOutput,
    EvidenceItem,
    ValidatedCase,
)


# Configurable MVP demonstration assumptions, not official policy.
HIGH_CONCERN_THRESHOLD = 75
MODERATE_CONCERN_THRESHOLD = 85

HIGH_CONCERN_SCORE = 30
MODERATE_CONCERN_SCORE = 15


def evaluate_attendance(validated_case: ValidatedCase) -> AgentOutput:
    """Evaluate attendance only; do not make the final support decision."""

    attendance = validated_case.attendance_rate

    if attendance is None:
        return AgentOutput(
            agent_name="Attendance Agent",
            status="NEEDS_INFORMATION",
            summary="Attendance evidence is unavailable.",
            score=0,
            flag="UNAVAILABLE",
            evidence=[
                EvidenceItem(
                    source="student_case",
                    detail="Attendance rate was not supplied.",
                )
            ],
            output_data={
                "attendance_rate": None,
                "threshold_type": "demo_assumption",
            },
        )

    if attendance < HIGH_CONCERN_THRESHOLD:
        flag = "HIGH"
        score = HIGH_CONCERN_SCORE
        summary = "Attendance is below the high-concern demo threshold."

    elif attendance < MODERATE_CONCERN_THRESHOLD:
        flag = "MODERATE"
        score = MODERATE_CONCERN_SCORE
        summary = "Attendance is in the moderate-concern demo range."

    else:
        flag = "NONE"
        score = 0
        summary = "No attendance concern was identified by the demo thresholds."

    return AgentOutput(
        agent_name="Attendance Agent",
        status="COMPLETED",
        summary=summary,
        score=score,
        flag=flag,
        evidence=[
            EvidenceItem(
                source="student_case.attendance_rate",
                detail=f"Supplied attendance rate: {attendance}%.",
                value=attendance,
            ),
            EvidenceItem(
                source="attendance_demo_thresholds",
                detail=(
                    "Demo assumptions: below 75% is high concern; "
                    "75% to below 85% is moderate concern; "
                    "85% or above has no attendance concern."
                ),
            ),
        ],
        output_data={
            "attendance_rate": attendance,
            "threshold_type": "demo_assumption",
            "high_threshold": HIGH_CONCERN_THRESHOLD,
            "moderate_threshold": MODERATE_CONCERN_THRESHOLD,
        },
    )

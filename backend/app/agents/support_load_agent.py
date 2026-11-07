"""Support Load Agent: evaluates missed submissions and unresolved tickets."""

from backend.app.models.schemas import (
    AgentOutput,
    EvidenceItem,
    ValidatedCase,
)


# Configurable MVP demonstration assumptions, not official policy.
HIGH_MISSED_SUBMISSIONS = 2
HIGH_UNRESOLVED_TICKETS = 2

MISSED_SUBMISSIONS_HIGH_SCORE = 30
MISSED_SUBMISSIONS_MODERATE_SCORE = 15
TICKETS_HIGH_SCORE = 20
TICKETS_MODERATE_SCORE = 10


def evaluate_support_load(validated_case: ValidatedCase) -> AgentOutput:
    """Evaluate workload indicators and report missing evidence."""

    missed = validated_case.missed_submissions
    tickets = validated_case.unresolved_support_tickets

    missing_fields = []
    evidence = []
    total_score = 0
    flags = []

    if missed is None:
        missing_fields.append("missed_submissions")
        missed_flag = "UNAVAILABLE"
    elif missed >= HIGH_MISSED_SUBMISSIONS:
        missed_flag = "HIGH"
        total_score += MISSED_SUBMISSIONS_HIGH_SCORE
    elif missed == 1:
        missed_flag = "MODERATE"
        total_score += MISSED_SUBMISSIONS_MODERATE_SCORE
    else:
        missed_flag = "NONE"

    if missed is not None:
        evidence.append(
            EvidenceItem(
                source="student_case.missed_submissions",
                detail=f"Missed submissions: {missed}.",
                value=missed,
            )
        )

    if tickets is None:
        missing_fields.append("unresolved_support_tickets")
        tickets_flag = "UNAVAILABLE"
    elif tickets >= HIGH_UNRESOLVED_TICKETS:
        tickets_flag = "HIGH"
        total_score += TICKETS_HIGH_SCORE
    elif tickets == 1:
        tickets_flag = "MODERATE"
        total_score += TICKETS_MODERATE_SCORE
    else:
        tickets_flag = "NONE"

    if tickets is not None:
        evidence.append(
            EvidenceItem(
                source="student_case.unresolved_support_tickets",
                detail=f"Unresolved support tickets: {tickets}.",
                value=tickets,
            )
        )

    flags.extend([missed_flag, tickets_flag])

    evidence.append(
        EvidenceItem(
            source="support_load_demo_thresholds",
            detail=(
                "Demo assumptions: 2 or more missed submissions = "
                "high (30 points); 1 = moderate (15 points). "
                "2 or more unresolved tickets = high (20 points); "
                "1 = moderate (10 points)."
            ),
        )
    )

    if missing_fields:
        status = "NEEDS_INFORMATION"
        summary = (
            "Support load evaluated partially; some evidence is unavailable."
        )
    else:
        status = "COMPLETED"
        summary = "Missed submissions and unresolved tickets evaluated."

    overall_flag = (
        "HIGH" if "HIGH" in flags
        else "MODERATE" if "MODERATE" in flags
        else "UNAVAILABLE" if "UNAVAILABLE" in flags
        else "NONE"
    )

    return AgentOutput(
        agent_name="Support Load Agent",
        status=status,
        summary=summary,
        score=total_score,
        flag=overall_flag,
        evidence=evidence,
        output_data={
            "missed_submissions_flag": missed_flag,
            "unresolved_tickets_flag": tickets_flag,
            "missing_fields": missing_fields,
            "threshold_type": "demo_assumption",
        },
    )

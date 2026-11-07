"""Engagement Agent: evaluates recent participation and inactivity."""

from backend.app.models.schemas import (
    AgentOutput,
    EvidenceItem,
    ValidatedCase,
)


# Configurable MVP demonstration assumptions, not official policy.
HIGH_CONCERN_DAYS = 14
MODERATE_CONCERN_DAYS = 7

HIGH_CONCERN_SCORE = 20
MODERATE_CONCERN_SCORE = 10


def evaluate_engagement(validated_case: ValidatedCase) -> AgentOutput:
    """Evaluate engagement evidence without making a final support decision."""

    days = validated_case.days_since_last_activity
    status = validated_case.engagement_status

    inconsistencies = []

    if (
        days is not None
        and status is not None
        and status.value == "active"
        and days >= HIGH_CONCERN_DAYS
    ):
        inconsistencies.append(
            "Engagement status is active, but the last recorded activity "
            f"was {days} days ago."
        )

    if (
        days is not None
        and status is not None
        and status.value == "inactive"
        and days < MODERATE_CONCERN_DAYS
    ):
        inconsistencies.append(
            "Engagement status is inactive, but recorded activity was "
            f"only {days} days ago."
        )

    if days is None:
        return AgentOutput(
            agent_name="Engagement Agent",
            status="NEEDS_INFORMATION",
            summary="Days since last activity are unavailable.",
            score=0,
            flag="UNAVAILABLE",
            evidence=[
                EvidenceItem(
                    source="student_case.days_since_last_activity",
                    detail="Inactivity duration was not supplied.",
                ),
                EvidenceItem(
                    source="student_case.engagement_status",
                    detail=(
                        f"Supplied engagement status: {status.value}"
                        if status is not None
                        else "Engagement status was not supplied."
                    ),
                ),
            ],
            output_data={
                "days_since_last_activity": None,
                "engagement_status": status.value if status else None,
                "threshold_type": "demo_assumption",
            },
        )

    if days >= HIGH_CONCERN_DAYS:
        flag = "HIGH"
        score = HIGH_CONCERN_SCORE
        summary = "Recent activity is at or beyond the high-concern demo threshold."

    elif days >= MODERATE_CONCERN_DAYS:
        flag = "MODERATE"
        score = MODERATE_CONCERN_SCORE
        summary = "Recent activity is in the moderate-concern demo range."

    else:
        flag = "NONE"
        score = 0
        summary = "No inactivity concern was identified by the demo thresholds."

    evidence = [
        EvidenceItem(
            source="student_case.days_since_last_activity",
            detail=f"Days since last recorded activity: {days}.",
            value=days,
        )
    ]

    if status is not None:
        evidence.append(
            EvidenceItem(
                source="student_case.engagement_status",
                detail=f"Supplied engagement status: {status.value}.",
                value=status.value,
            )
        )

    evidence.append(
        EvidenceItem(
            source="engagement_demo_thresholds",
            detail=(
                "Demo assumptions: 14 or more days is high concern; "
                "7 to 13 days is moderate concern; "
                "below 7 days has no inactivity concern."
            ),
        )
    )

    return AgentOutput(
        agent_name="Engagement Agent",
        status="COMPLETED",
        summary=summary,
        score=score,
        flag=flag,
        evidence=evidence,
        output_data={
            "days_since_last_activity": days,
            "engagement_status": status.value if status else None,
            "threshold_type": "demo_assumption",
            "high_threshold_days": HIGH_CONCERN_DAYS,
            "moderate_threshold_days": MODERATE_CONCERN_DAYS,
            "inconsistencies": inconsistencies,
        },
    )

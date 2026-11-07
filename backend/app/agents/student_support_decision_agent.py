"""Student Support Decision Agent: applies deterministic support rules."""

from backend.app.models.schemas import (
    AgentOutput,
    EvidenceItem,
    FinalRecommendation,
    RecommendationAction,
    ValidatedCase,
)


def make_decision(
    validated_case: ValidatedCase,
    attendance_output: AgentOutput,
    engagement_output: AgentOutput,
    support_output: AgentOutput,
    inconsistencies: list[str] | None = None,
    intake_output: AgentOutput | None = None,
) -> FinalRecommendation:
    """Combine specialist outputs into a transparent support recommendation."""

    inconsistencies = inconsistencies or []

    outputs = [
        attendance_output,
        engagement_output,
        support_output,
    ]

    output_refs = (
        [intake_output.agent_name] if intake_output is not None else []
    ) + [output.agent_name for output in outputs]

    # Rule 1: incomplete specialist evidence must not produce a final priority.
    incomplete_agents = [
        output.agent_name
        for output in outputs
        if output.status != "COMPLETED"
    ]

    if incomplete_agents:
        return FinalRecommendation(
            action=RecommendationAction.REQUEST_MORE_INFO,
            priority_score=min(sum(o.score for o in outputs), 100),
            priority_band="INFORMATION_REQUIRED",
            reasons=[
                "Essential support evidence is incomplete.",
                "Additional information is required before prioritization.",
            ],
            triggered_rules=["RULE-01-INCOMPLETE-EVIDENCE"],
            evidence=[
                EvidenceItem(
                    source="decision_agent",
                    detail=f"Incomplete evidence from: {', '.join(incomplete_agents)}.",
                )
            ],
            agent_output_refs=output_refs,
        )

    # Rule 2: explicitly reported inconsistencies require human review.
    if inconsistencies:
        return FinalRecommendation(
            action=RecommendationAction.TUTOR_REVIEW,
            priority_score=min(sum(o.score for o in outputs), 100),
            priority_band="REVIEW_REQUIRED",
            reasons=[
                "The supplied support evidence contains inconsistencies.",
                "A tutor should review the case before outreach prioritization.",
            ],
            triggered_rules=["RULE-02-INCONSISTENT-EVIDENCE"],
            evidence=[
                EvidenceItem(
                    source="decision_agent",
                    detail=issue,
                )
                for issue in inconsistencies
            ],
            agent_output_refs=output_refs,
        )

    # Rule 3: the specific Product Bible priority combination.
    priority_combination = (
        validated_case.attendance_rate is not None
        and validated_case.attendance_rate < 75
        and validated_case.missed_submissions is not None
        and validated_case.missed_submissions >= 2
    )

    total_score = min(sum(output.score for output in outputs), 100)

    evidence_outputs = (
        ([intake_output] if intake_output is not None else []) + outputs
    )
    all_evidence = [
        evidence
        for output in evidence_outputs
        for evidence in output.evidence
    ]

    if priority_combination:
        return FinalRecommendation(
            action=RecommendationAction.PRIORITY_OUTREACH,
            priority_score=total_score,
            priority_band="HIGH",
            reasons=[
                "Attendance is below the configured 75% demo threshold.",
                "The case has at least two missed submissions.",
                "Both indicators together trigger the priority outreach rule.",
            ],
            triggered_rules=["RULE-03-LOW-ATTENDANCE-AND-MISSED-WORK"],
            evidence=all_evidence,
            agent_output_refs=output_refs,
        )

    # Rule 4: multiple concerns or any isolated high concern require tutor review.
    concern_flags = [
        attendance_output.flag,
        engagement_output.flag,
        support_output.output_data.get("missed_submissions_flag"),
        support_output.output_data.get("unresolved_tickets_flag"),
    ]

    active_concerns = [
        flag for flag in concern_flags
        if flag in ("HIGH", "MODERATE")
    ]

    if len(active_concerns) >= 2 or "HIGH" in active_concerns:
        reasons = []

        if len(active_concerns) >= 2:
            reasons.append("Multiple support concerns were identified.")

        if "HIGH" in active_concerns:
            reasons.append(
                "A high-concern indicator requires individual tutor review."
            )

        return FinalRecommendation(
            action=RecommendationAction.TUTOR_REVIEW,
            priority_score=total_score,
            priority_band="REVIEW_REQUIRED",
            reasons=reasons,
            triggered_rules=["RULE-04-MULTIPLE-OR-HIGH-CONCERNS"],
            evidence=all_evidence,
            agent_output_refs=output_refs,
        )

    # Rule 5: no major concern or one mild concern.
    return FinalRecommendation(
        action=RecommendationAction.NORMAL_FOLLOWUP,
        priority_score=total_score,
        priority_band="NORMAL",
        reasons=[
            "No major support concern was identified.",
            "Normal follow-up is appropriate based on the available evidence.",
        ],
        triggered_rules=["RULE-05-NORMAL-FOLLOWUP"],
        evidence=all_evidence,
        agent_output_refs=output_refs,
    )

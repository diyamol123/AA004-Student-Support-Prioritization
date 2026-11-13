"""Pydantic schemas for the AA004 Student Support Prioritization MVP."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EngagementStatus(str, Enum):
    ACTIVE = "active"
    LOW = "low"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class RecommendationAction(str, Enum):
    NORMAL_FOLLOWUP = "NORMAL_FOLLOWUP"
    PRIORITY_OUTREACH = "PRIORITY_OUTREACH"
    TUTOR_REVIEW = "TUTOR_REVIEW"
    REQUEST_MORE_INFO = "REQUEST_MORE_INFO"


class StudentCaseInput(BaseModel):
    """Business input. Optional evidence allows incomplete cases to be identified."""

    case_id: str = Field(min_length=1, description="Non-identifying support case reference")
    attendance_rate: float | None = Field(default=None, ge=0, le=100)
    missed_submissions: int | None = Field(default=None, ge=0)
    engagement_status: EngagementStatus | None = None
    days_since_last_activity: int | None = Field(default=None, ge=0)
    unresolved_support_tickets: int | None = Field(default=None, ge=0)
    recent_activity_indicators: list[str] = Field(default_factory=list)


class ValidatedCase(BaseModel):
    """Normalized case data produced by the Case Intake Agent."""

    case_id: str
    attendance_rate: float | None = None
    missed_submissions: int | None = None
    engagement_status: EngagementStatus | None = None
    days_since_last_activity: int | None = None
    unresolved_support_tickets: int | None = None
    recent_activity_indicators: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    """A traceable fact used by an agent or decision rule."""

    source: str
    detail: str
    value: str | int | float | bool | None = None


class AgentOutput(BaseModel):
    """Common structured output contract for each specialized agent."""

    agent_name: str
    status: str
    summary: str
    score: int = Field(default=0, ge=0, le=100)
    flag: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    output_data: dict[str, Any] = Field(default_factory=dict)


class FinalRecommendation(BaseModel):
    action: RecommendationAction
    priority_score: int = Field(ge=0, le=100)
    priority_band: str
    reasons: list[str] = Field(default_factory=list)
    triggered_rules: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    agent_output_refs: list[str] = Field(default_factory=list)


class LLMExplanation(BaseModel):
    """Validated, non-authoritative AI explanation."""

    summary: str = Field(min_length=1, max_length=500)
    reasons: list[str] = Field(default_factory=list, max_length=5)
    confidence_note: str = Field(min_length=1, max_length=300)


class LLMTraceMetadata(BaseModel):
    """Safe metadata describing the optional LLM invocation."""

    llm_used: bool = False
    provider: str = "gemini"
    model: str = "gemini-3.5-flash-lite"
    status: str = "NOT_CONFIGURED"
    fallback_used: bool = True
    validation_status: str = "NOT_RUN"
    error_category: str | None = None


class WorkflowContext(BaseModel):
    """Shared context scoped to one workflow execution; not long-term memory."""

    workflow_id: str
    student_case: StudentCaseInput
    validated_case: ValidatedCase | None = None
    attendance_flag: str | None = None
    engagement_flag: str | None = None
    support_load_flag: str | None = None
    scores: dict[str, int] = Field(default_factory=dict)
    agent_outputs: list[AgentOutput] = Field(default_factory=list)
    final_recommendation: FinalRecommendation | None = None
    explanation: list[str] = Field(default_factory=list)
    llm_metadata: LLMTraceMetadata = Field(
        default_factory=LLMTraceMetadata
    )

    audit_reference: str | None = None
    node_trace: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

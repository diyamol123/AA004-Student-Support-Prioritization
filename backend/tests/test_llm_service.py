"""Evaluation tests for the controlled Gemini explanation service."""

from pydantic import ValidationError

from backend.app.models.schemas import LLMExplanation
from backend.app.services import llm_service


def setup_function():
    import os
    os.environ["LLM_ENABLED"] = "true"
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["LLM_MODEL"] = "gemini-3.5-flash-lite"
    os.environ["GEMINI_API_KEY"] = "test-key"


def test_valid_gemini_response(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "_invoke_gemini",
        lambda facts: LLMExplanation(
            summary="The existing recommendation is supported.",
            reasons=["Attendance evidence supports the decision."],
            confidence_note="Based only on supplied evidence.",
        ),
    )

    explanation, metadata = llm_service.generate_explanation(
        ["Priority score: 80"],
        ["Deterministic fallback"],
    )

    assert explanation[0] == "The existing recommendation is supported."
    assert metadata.llm_used is True
    assert metadata.fallback_used is False
    assert metadata.validation_status == "VALID"


def test_ambiguous_input_is_passed_as_facts(monkeypatch):
    received = []

    def fake_invoke(facts):
        received.extend(facts)
        return LLMExplanation(
            summary="The available evidence is limited.",
            reasons=["Some information is unclear."],
            confidence_note="No additional facts were assumed.",
        )

    monkeypatch.setattr(llm_service, "_invoke_gemini", fake_invoke)

    explanation, metadata = llm_service.generate_explanation(
        ["Attendance evidence is incomplete"],
        ["Deterministic fallback"],
    )

    assert received == ["Attendance evidence is incomplete"]
    assert metadata.llm_used is True
    assert "limited" in explanation[0]


def test_timeout_uses_deterministic_fallback(monkeypatch):
    def timeout(_facts):
        raise TimeoutError("Simulated timeout")

    monkeypatch.setattr(llm_service, "_invoke_gemini", timeout)

    explanation, metadata = llm_service.generate_explanation(
        ["Priority score: 90"],
        ["Original deterministic explanation"],
    )

    assert explanation == ["Original deterministic explanation"]
    assert metadata.status == "TIMEOUT"
    assert metadata.fallback_used is True


def test_invalid_output_uses_deterministic_fallback(monkeypatch):
    def invalid(_facts):
        return LLMExplanation.model_validate({
            "summary": "",
            "reasons": [],
            "confidence_note": "Invalid summary",
        })

    monkeypatch.setattr(llm_service, "_invoke_gemini", invalid)

    explanation, metadata = llm_service.generate_explanation(
        ["Priority score: 50"],
        ["Safe deterministic explanation"],
    )

    assert explanation == ["Safe deterministic explanation"]
    assert metadata.status == "INVALID_OUTPUT"
    assert metadata.validation_status == "FAILED"


def test_incomplete_case_edge_case(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "_invoke_gemini",
        lambda facts: LLMExplanation(
            summary="The recommendation uses incomplete evidence.",
            reasons=["Some required information is missing."],
            confidence_note="No missing information was inferred.",
        ),
    )

    explanation, metadata = llm_service.generate_explanation(
        ["Selected route: INCOMPLETE", "Attendance rate: None"],
        ["Deterministic incomplete-case explanation"],
    )

    assert metadata.llm_used is True
    assert "incomplete" in explanation[0].lower()

"""Prevent real Gemini requests during general workflow tests."""

import pytest

from backend.app.graphs import student_support_graph as graph_module
from backend.app.models.schemas import LLMTraceMetadata


@pytest.fixture(autouse=True)
def mock_llm_for_workflow_tests(monkeypatch):
    def deterministic_fallback(facts, fallback_explanation):
        return fallback_explanation, LLMTraceMetadata(
            llm_used=False,
            status="TEST_FALLBACK",
            fallback_used=True,
            validation_status="NOT_RUN",
        )

    monkeypatch.setattr(
        graph_module,
        "generate_explanation",
        deterministic_fallback,
    )

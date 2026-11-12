"""Controlled Gemini explanation service with deterministic fallback."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.app.models.schemas import (
    LLMExplanation,
    LLMTraceMetadata,
)

load_dotenv(dotenv_path=Path.cwd() / ".env")


def _invoke_gemini(facts: list[str]) -> LLMExplanation:
    """Generate a structured explanation using only supplied facts."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("MISSING_API_KEY")

    model = os.getenv("LLM_MODEL", "gemini-3.8-flash")
    timeout = int(os.getenv("LLM_TIMEOUT", "12"))

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=timeout * 1000),
    )

    prompt = f"""
You are an explanation assistant for a student support workflow.

Your ONLY task is to explain an existing deterministic recommendation.

Rules:
- Use only the supplied facts.
- Do not change scores, priority, decisions, or recommendations.
- Do not invent evidence or student information.
- Do not make a new support decision.
- Keep the explanation concise and factual.

Supplied facts:
{facts}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LLMExplanation,
        ),
    )

    if not response.text:
        raise ValueError("Empty model response")

    return LLMExplanation.model_validate_json(response.text)


def generate_explanation(
    facts: list[str],
    fallback_explanation: list[str],
) -> tuple[list[str], LLMTraceMetadata]:
    """Use Gemini when available; otherwise preserve deterministic output."""

    provider = os.getenv("LLM_PROVIDER", "gemini")
    model = os.getenv("LLM_MODEL", "gemini-3.8-flash")
    enabled = os.getenv("LLM_ENABLED", "false").lower() in {
        "true",
        "1",
        "yes",
    }

    def fallback(status: str, error: str | None = None):
        return fallback_explanation, LLMTraceMetadata(
            llm_used=False,
            provider=provider,
            model=model,
            status=status,
            fallback_used=True,
            validation_status="FAILED" if error else "NOT_RUN",
            error_category=error,
        )

    if not enabled:
        return fallback("DISABLED")

    if provider != "gemini":
        return fallback("UNSUPPORTED_PROVIDER", "ConfigurationError")

    if not os.getenv("GEMINI_API_KEY"):
        return fallback("MISSING_API_KEY", "ConfigurationError")

    try:
        result = _invoke_gemini(facts)

        return (
            [
                result.summary,
                *result.reasons,
                result.confidence_note,
            ],
            LLMTraceMetadata(
                llm_used=True,
                provider=provider,
                model=model,
                status="SUCCESS",
                fallback_used=False,
                validation_status="VALID",
            ),
        )

    except ValidationError:
        return fallback("INVALID_OUTPUT", "ValidationError")

    except Exception as exc:
        error_name = type(exc).__name__
        error_message = str(exc).upper()

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return fallback("QUOTA_EXCEEDED", "QuotaExceeded")

        if "TIMEOUT" in error_name.upper():
            return fallback("TIMEOUT", "TimeoutError")

        return fallback("ERROR", error_name)

import json
import os
import re
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException, status

from schemas import MasteryLevel

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RUBRIC_PATH = Path(__file__).resolve().parent / "rubric.md"
MODEL_NAME = "gemini-3.5-flash-lite"

ALLOWED_LEVELS = {level.value for level in MasteryLevel}


def load_rubric() -> str:
    if not RUBRIC_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rubric file not found",
        )
    return RUBRIC_PATH.read_text(encoding="utf-8")


def _build_system_instruction(rubric: str) -> str:
    return f"""You are a strict grader for skill assessments.

Grade the student's submission using ONLY the rubric below.
Award the highest mastery level whose criteria are fully satisfied.
If Level 1 is not met, use "Not Demonstrated".

RUBRIC:
{rubric}

Respond ONLY with valid JSON (no markdown, no extra text) using exactly these fields:
{{
  "competency": "<string: name of the competency being assessed>",
  "mastery_level": "<one of: Not Demonstrated, Level 1, Level 2, Level 3>",
  "confidence": <float between 0 and 1>,
  "feedback": "<string explaining the score>"
}}
"""


def parse_llm_json(text: str) -> dict:
    """Parse JSON from an LLM response, including markdown code-fence wrappers."""
    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    else:
        # Fallback: extract outermost JSON object if present
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to parse model JSON response: {exc}",
        ) from exc

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model response JSON must be an object",
        )
    return data


def _validate_assessment_payload(data: dict) -> dict:
    required = {"competency", "mastery_level", "confidence", "feedback"}
    missing = required - data.keys()
    if missing:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Model response missing fields: {sorted(missing)}",
        )

    mastery = data["mastery_level"]
    if mastery not in ALLOWED_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid mastery_level from model: {mastery}",
        )

    try:
        confidence = float(data["confidence"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="confidence must be a float between 0 and 1",
        ) from exc

    if not 0.0 <= confidence <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="confidence must be a float between 0 and 1",
        )

    competency = str(data["competency"]).strip()
    feedback = str(data["feedback"]).strip()
    if not competency or not feedback:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="competency and feedback must be non-empty strings",
        )

    return {
        "competency": competency,
        "mastery_level": mastery,
        "confidence": confidence,
        "feedback": feedback,
    }


def grade_submission(submission_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY environment variable is not set",
        )

    rubric = load_rubric()
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=_build_system_instruction(rubric),
    )

    try:
        response = model.generate_content(
            f"Student submission:\n\n{submission_text}",
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )
        raw_text = response.text
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API error: {exc}",
        ) from exc

    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Empty response from Gemini API",
        )

    parsed = parse_llm_json(raw_text)
    return _validate_assessment_payload(parsed)

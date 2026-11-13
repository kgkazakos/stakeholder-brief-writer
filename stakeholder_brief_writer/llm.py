"""LLM enrichment for stakeholder-brief-writer.

Enhances extracted briefs with polished narrative summaries,
refined finding statements, and priority rationale.
Uses LiteLLM for model-agnostic multi-backend support.

LLM enrichment is ON by default. The tool degrades gracefully
when no API key is present — core metrics are never modified.
"""

from __future__ import annotations

import json
import logging

from .models import ExecutiveBrief

logger = logging.getLogger(__name__)

# Locked model strings (CPR standard)
DEFAULT_MODELS = [
    "anthropic/claude-opus-4-7",
    "gemini/gemini-4-argon",
    "openai/gpt-5.5",
]

_SYSTEM_PROMPT = """You are an expert UX research communicator.
Your task is to polish a structured executive brief for a non-technical stakeholder audience.

Rules:
- Respond ONLY with valid JSON — no markdown, no preamble.
- Do NOT invent findings not present in the input.
- Keep narrative_summary under 120 words.
- refined_findings must contain the same count as input findings.
- confidence_rationale should be 1–2 sentences max.
- All fields are required."""

_USER_TEMPLATE = """Given this structured brief, return a JSON object with:
- "narrative_summary": a crisp 80–120 word executive narrative (past tense, stakeholder-facing)
- "refined_findings": list of improved finding statements (same count, sharper language)
- "confidence_rationale": one sentence explaining overall confidence level
- "tag_suggestions": list of 2–4 thematic tags for the brief

Brief input:
{brief_json}"""


def enrich_brief(
    brief: ExecutiveBrief,
    model: str = DEFAULT_MODELS[0],
    llm_enabled: bool = True,
) -> ExecutiveBrief:
    """Enrich an ExecutiveBrief with LLM-polished narrative and tags.

    Always returns the brief unchanged if LLM is disabled or fails.
    Core rule-based metrics (findings, recommendations) are never overwritten.
    """
    if not llm_enabled:
        return brief

    try:
        import litellm  # noqa: PLC0415

        brief_json = json.dumps(
            {
                "title": brief.title,
                "study_type": brief.study_type,
                "participant_summary": brief.participant_summary,
                "top_findings": [f.statement for f in brief.top_findings],
                "recommendations": [r.action for r in brief.recommendations],
                "limitations": brief.limitations,
                "confidence_overall": brief.confidence_overall.value,
            },
            indent=2,
        )

        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _USER_TEMPLATE.format(brief_json=brief_json)},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)

        # Apply enrichments — additive only, never overwrite core data
        if "narrative_summary" in data:
            brief.narrative_summary = data["narrative_summary"]
        if "confidence_rationale" in data:
            brief.narrative_summary += f" {data['confidence_rationale']}"
        if "refined_findings" in data and len(data["refined_findings"]) == len(brief.top_findings):
            for finding, refined in zip(brief.top_findings, data["refined_findings"]):
                finding.statement = refined
        if "tag_suggestions" in data:
            for finding in brief.top_findings:
                finding.tags = data.get("tag_suggestions", [])[:4]

        brief.llm_enriched = True
        brief.llm_model = model
        brief.word_count = len(brief.narrative_summary.split())

    except ImportError:
        logger.warning("litellm not installed — skipping LLM enrichment.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM enrichment failed (%s) — using rule-based output.", exc)

    return brief

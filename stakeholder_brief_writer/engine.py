"""Rule-based engine for stakeholder-brief-writer.

Extracts structure from a full research report using heuristics —
no LLM required. Produces an ExecutiveBrief suitable for one-page output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import (
    ConfidenceLevel,
    ExecutiveBrief,
    ImpactScope,
    Recommendation,
    ResearchFinding,
)

# ---------------------------------------------------------------------------
# Section detection patterns
# ---------------------------------------------------------------------------

_FINDING_HEADERS = re.compile(
    r"(?i)^\s*#*\s*(key\s+findings?|findings?|results?|what\s+we\s+found|insights?)\s*:?\s*$",
    re.MULTILINE,
)
_RECOMMENDATION_HEADERS = re.compile(
    r"(?i)^\s*#*\s*(recommendations?|next\s+steps?|actions?|what\s+to\s+do)\s*:?\s*$",
    re.MULTILINE,
)
_QUESTION_HEADERS = re.compile(
    r"(?i)^\s*#*\s*(research\s+questions?|study\s+goals?|objectives?)\s*:?\s*$",
    re.MULTILINE,
)
_LIMITATION_HEADERS = re.compile(
    r"(?i)^\s*#*\s*(limitations?|caveats?|constraints?)\s*:?\s*$",
    re.MULTILINE,
)
_METRIC_PATTERN = re.compile(
    r"(?:n\s*=\s*(\d+)|(\d+)\s*participants?|(\d+)%|sat(?:isfaction)?\s*score\s*[:=]\s*([\d.]+)|sus\s*[:=]\s*([\d.]+))",
    re.IGNORECASE,
)
_BULLET_LINE = re.compile(r"^\s*[-*•·]\s+(.+)$", re.MULTILINE)
_NUMBERED_LINE = re.compile(r"^\s*\d+[.)]\s+(.+)$", re.MULTILINE)
_CONFIDENCE_WORDS = {
    "strong": ConfidenceLevel.HIGH,
    "clear": ConfidenceLevel.HIGH,
    "definitive": ConfidenceLevel.HIGH,
    "robust": ConfidenceLevel.HIGH,
    "suggest": ConfidenceLevel.MEDIUM,
    "indicate": ConfidenceLevel.MEDIUM,
    "appear": ConfidenceLevel.MEDIUM,
    "preliminary": ConfidenceLevel.LOW,
    "tentative": ConfidenceLevel.LOW,
    "exploratory": ConfidenceLevel.LOW,
    "limited": ConfidenceLevel.LOW,
}


def _detect_confidence(text: str) -> ConfidenceLevel:
    lower = text.lower()
    for word, level in _CONFIDENCE_WORDS.items():
        if word in lower:
            return level
    return ConfidenceLevel.MEDIUM


def _detect_impact_scope(text: str) -> ImpactScope:
    lower = text.lower()
    if any(w in lower for w in ["strategy", "vision", "roadmap", "market", "competitive"]):
        return ImpactScope.STRATEGIC
    if any(w in lower for w in ["process", "workflow", "daily", "team", "sprint"]):
        return ImpactScope.OPERATIONAL
    return ImpactScope.TACTICAL


def _extract_bullets(text: str) -> list[str]:
    bullets = [m.group(1).strip() for m in _BULLET_LINE.finditer(text)]
    numbered = [m.group(1).strip() for m in _NUMBERED_LINE.finditer(text)]
    return bullets + numbered


def _extract_section(text: str, header_pattern: re.Pattern, max_chars: int = 2000) -> str:
    """Extract text between a matched header and the next header-like line."""
    match = header_pattern.search(text)
    if not match:
        return ""
    start = match.end()
    # Find next markdown heading or blank-line-then-capital sequence
    next_section = re.search(r"\n#{1,3}\s+\w", text[start : start + max_chars])
    end = start + (next_section.start() if next_section else max_chars)
    return text[start:end].strip()


def _extract_metrics(text: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for m in _METRIC_PATTERN.finditer(text):
        if m.group(1):
            metrics["n"] = m.group(1)
        if m.group(2):
            metrics["participants"] = m.group(2)
        if m.group(4):
            metrics["satisfaction_score"] = m.group(4)
        if m.group(5):
            metrics["sus_score"] = m.group(5)
    return metrics


def _infer_study_type(text: str) -> str:
    lower = text.lower()
    if "interview" in lower and "survey" in lower:
        return "Mixed-methods (interviews + survey)"
    if "interview" in lower:
        return "Qualitative (interviews)"
    if "survey" in lower or "questionnaire" in lower:
        return "Quantitative (survey)"
    if "usability" in lower or "think aloud" in lower:
        return "Usability study"
    if "diary" in lower or "longitudinal" in lower:
        return "Longitudinal / diary study"
    return "Research study"


def _infer_participant_summary(text: str, metrics: dict[str, str]) -> str:
    n = metrics.get("participants") or metrics.get("n", "")
    lower = text.lower()
    roles = []
    for term in ["manager", "developer", "designer", "researcher", "user", "customer", "analyst"]:
        if term in lower:
            roles.append(term + "s")
    role_str = ", ".join(roles[:2]) if roles else "participants"
    if n:
        return f"{n} {role_str}"
    return f"Multiple {role_str}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass
class BriefConfig:
    max_findings: int = 5
    max_recommendations: int = 4
    max_next_steps: int = 3
    target_word_count: int = 350


def generate_brief(report_text: str, config: BriefConfig | None = None) -> ExecutiveBrief:
    """Generate an ExecutiveBrief from a full research report."""
    if config is None:
        config = BriefConfig()

    # --- Study metadata ---
    study_type = _infer_study_type(report_text)
    metrics = _extract_metrics(report_text)
    participant_summary = _infer_participant_summary(report_text, metrics)

    # --- Research questions ---
    q_section = _extract_section(report_text, _QUESTION_HEADERS)
    research_questions = _extract_bullets(q_section)[:3]
    if not research_questions:
        # Fallback: look for question marks in first 500 chars
        sentences = re.split(r"[.!?]", report_text[:800])
        research_questions = [s.strip() for s in sentences if "?" in s and len(s.strip()) > 15][:2]

    # --- Findings ---
    f_section = _extract_section(report_text, _FINDING_HEADERS)
    raw_findings = _extract_bullets(f_section)[: config.max_findings]
    if not raw_findings:
        # Fallback: split on paragraphs and take first N non-empty
        paras = [p.strip() for p in report_text.split("\n\n") if p.strip() and len(p.strip()) > 40]
        raw_findings = paras[1 : config.max_findings + 1]

    findings = []
    for raw in raw_findings:
        # Split into statement + evidence if semicolon present
        parts = raw.split(";", 1)
        stmt = parts[0].strip()
        evidence = parts[1].strip() if len(parts) > 1 else ""
        findings.append(
            ResearchFinding(
                statement=stmt,
                evidence=evidence,
                confidence=_detect_confidence(raw),
                impact_scope=_detect_impact_scope(raw),
                tags=[],
            )
        )

    # --- Recommendations ---
    r_section = _extract_section(report_text, _RECOMMENDATION_HEADERS)
    raw_recs = _extract_bullets(r_section)[: config.max_recommendations]
    recommendations = []
    for i, raw in enumerate(raw_recs):
        recommendations.append(
            Recommendation(
                action=raw,
                rationale="",
                priority=i + 1 if i < 3 else 3,
            )
        )

    # --- Limitations ---
    l_section = _extract_section(report_text, _LIMITATION_HEADERS)
    limitations = _extract_bullets(l_section)[:3]

    # --- Next steps ---
    ns_section = _extract_section(
        report_text,
        re.compile(
            r"(?i)^\s*#*\s*(next\s+steps?|follow.?up|future\s+work)\s*:?\s*$",
            re.MULTILINE,
        ),
    )
    next_steps = _extract_bullets(ns_section)[: config.max_next_steps]
    if not next_steps and recommendations:
        next_steps = [r.action for r in recommendations[:2]]

    # --- Title ---
    first_line = report_text.strip().split("\n")[0].lstrip("#").strip()
    title = first_line[:80] if first_line else "Research Report"

    # --- Narrative summary (rule-based) ---
    narrative = (
        f"This {study_type.lower()} involved {participant_summary}. "
        f"The study surfaced {len(findings)} key finding(s) "
        f"with {len(recommendations)} actionable recommendation(s)."
    )

    brief = ExecutiveBrief(
        title=title,
        study_type=study_type,
        participant_summary=participant_summary,
        research_questions=research_questions,
        top_findings=findings,
        recommendations=recommendations,
        key_metrics=metrics,
        limitations=limitations,
        next_steps=next_steps,
        narrative_summary=narrative,
    )
    brief.word_count = len(brief.narrative_summary.split())
    return brief

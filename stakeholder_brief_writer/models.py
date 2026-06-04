"""Data models for stakeholder-brief-writer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactScope(str, Enum):
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"


@dataclass
class ResearchFinding:
    """A single research finding extracted from the report."""

    statement: str
    evidence: str
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    impact_scope: ImpactScope = ImpactScope.TACTICAL
    tags: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """An actionable recommendation for stakeholders."""

    action: str
    rationale: str
    priority: int = 2  # 1=high, 2=medium, 3=low
    owner_hint: str = ""
    timeline_hint: str = ""


@dataclass
class ExecutiveBrief:
    """The complete one-page executive brief."""

    title: str
    study_type: str
    participant_summary: str
    research_questions: list[str]
    top_findings: list[ResearchFinding]
    recommendations: list[Recommendation]
    key_metrics: dict[str, str]
    limitations: list[str]
    next_steps: list[str]
    word_count: int = 0
    llm_enriched: bool = False
    llm_model: str = ""
    narrative_summary: str = ""
    confidence_overall: ConfidenceLevel = ConfidenceLevel.MEDIUM

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "study_type": self.study_type,
            "participant_summary": self.participant_summary,
            "research_questions": self.research_questions,
            "top_findings": [
                {
                    "statement": f.statement,
                    "evidence": f.evidence,
                    "confidence": f.confidence.value,
                    "impact_scope": f.impact_scope.value,
                    "tags": f.tags,
                }
                for f in self.top_findings
            ],
            "recommendations": [
                {
                    "action": r.action,
                    "rationale": r.rationale,
                    "priority": r.priority,
                    "owner_hint": r.owner_hint,
                    "timeline_hint": r.timeline_hint,
                }
                for r in self.recommendations
            ],
            "key_metrics": self.key_metrics,
            "limitations": self.limitations,
            "next_steps": self.next_steps,
            "word_count": self.word_count,
            "llm_enriched": self.llm_enriched,
            "llm_model": self.llm_model,
            "narrative_summary": self.narrative_summary,
            "confidence_overall": self.confidence_overall.value,
        }

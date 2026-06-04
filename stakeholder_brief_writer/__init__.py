"""stakeholder-brief-writer — CPR Orbital Tool #39.

Auto-generates a one-page executive summary from a full research report.
"""

__version__ = "0.1.0"

from .engine import BriefConfig, generate_brief
from .export import to_json, to_markdown, to_text
from .models import (
    ConfidenceLevel,
    ExecutiveBrief,
    ImpactScope,
    Recommendation,
    ResearchFinding,
)

__all__ = [
    "generate_brief",
    "BriefConfig",
    "to_json",
    "to_markdown",
    "to_text",
    "ExecutiveBrief",
    "ResearchFinding",
    "Recommendation",
    "ConfidenceLevel",
    "ImpactScope",
]

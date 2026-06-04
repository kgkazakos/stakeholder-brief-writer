"""Tests for stakeholder-brief-writer."""

from __future__ import annotations

from pathlib import Path

import pytest

from stakeholder_brief_writer.engine import BriefConfig, generate_brief
from stakeholder_brief_writer.export import to_json, to_markdown, to_text
from stakeholder_brief_writer.models import (
    ConfidenceLevel,
    ExecutiveBrief,
    ImpactScope,
    Recommendation,
    ResearchFinding,
)

FIXTURE = Path(__file__).parent / "fixtures" / "checkout_research.md"
REPORT_TEXT = FIXTURE.read_text(encoding="utf-8")


# ── Engine tests ────────────────────────────────────────────────────────────

class TestGenerateBrief:
    def test_returns_executive_brief(self):
        brief = generate_brief(REPORT_TEXT)
        assert isinstance(brief, ExecutiveBrief)

    def test_title_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        assert "Checkout" in brief.title

    def test_study_type_detected(self):
        brief = generate_brief(REPORT_TEXT)
        assert brief.study_type  # non-empty string

    def test_participant_summary(self):
        brief = generate_brief(REPORT_TEXT)
        assert brief.participant_summary  # non-empty

    def test_findings_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        assert len(brief.top_findings) >= 1

    def test_findings_max_respected(self):
        config = BriefConfig(max_findings=3)
        brief = generate_brief(REPORT_TEXT, config)
        assert len(brief.top_findings) <= 3

    def test_recommendations_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        assert len(brief.recommendations) >= 1

    def test_recommendations_max_respected(self):
        config = BriefConfig(max_recommendations=2)
        brief = generate_brief(REPORT_TEXT, config)
        assert len(brief.recommendations) <= 2

    def test_research_questions_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        assert len(brief.research_questions) >= 1

    def test_limitations_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        assert len(brief.limitations) >= 1

    def test_next_steps_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        assert len(brief.next_steps) >= 1

    def test_metrics_extracted(self):
        brief = generate_brief(REPORT_TEXT)
        # n=12 should be found
        assert "participants" in brief.key_metrics or "n" in brief.key_metrics

    def test_narrative_summary_set(self):
        brief = generate_brief(REPORT_TEXT)
        assert brief.narrative_summary

    def test_llm_not_enriched_by_default(self):
        brief = generate_brief(REPORT_TEXT)
        assert brief.llm_enriched is False

    def test_confidence_levels_valid(self):
        brief = generate_brief(REPORT_TEXT)
        for f in brief.top_findings:
            assert f.confidence in ConfidenceLevel.__members__.values()

    def test_impact_scopes_valid(self):
        brief = generate_brief(REPORT_TEXT)
        for f in brief.top_findings:
            assert f.impact_scope in ImpactScope.__members__.values()

    def test_empty_report_graceful(self):
        brief = generate_brief("No structure here.")
        assert isinstance(brief, ExecutiveBrief)
        assert brief.title

    def test_minimal_report(self):
        text = "# Quick Study\n\nWe talked to 5 users. They found navigation confusing."
        brief = generate_brief(text)
        assert isinstance(brief, ExecutiveBrief)


# ── Export tests ────────────────────────────────────────────────────────────

class TestExports:
    @pytest.fixture
    def brief(self):
        return generate_brief(REPORT_TEXT)

    def test_to_markdown_returns_string(self, brief):
        md = to_markdown(brief)
        assert isinstance(md, str)
        assert "#" in md  # has markdown headings

    def test_to_markdown_contains_title(self, brief):
        md = to_markdown(brief)
        assert brief.title in md

    def test_to_markdown_contains_findings(self, brief):
        md = to_markdown(brief)
        assert "Key Findings" in md

    def test_to_json_valid(self, brief):
        import json
        j = to_json(brief)
        data = json.loads(j)
        assert "title" in data
        assert "top_findings" in data
        assert "recommendations" in data

    def test_to_json_findings_structure(self, brief):
        import json
        data = json.loads(to_json(brief))
        for f in data["top_findings"]:
            assert "statement" in f
            assert "confidence" in f
            assert "impact_scope" in f

    def test_to_text_returns_string(self, brief):
        txt = to_text(brief)
        assert isinstance(txt, str)
        assert brief.title.upper() in txt

    def test_to_markdown_writes_file(self, brief, tmp_path):
        p = tmp_path / "brief.md"
        to_markdown(brief, p)
        assert p.exists()
        assert p.read_text()

    def test_to_json_writes_file(self, brief, tmp_path):
        p = tmp_path / "brief.json"
        to_json(brief, p)
        assert p.exists()

    def test_to_text_writes_file(self, brief, tmp_path):
        p = tmp_path / "brief.txt"
        to_text(brief, p)
        assert p.exists()


# ── LLM enrichment tests (no API key required) ─────────────────────────────

class TestLLMEnrichment:
    def test_llm_disabled_returns_unchanged(self):
        from stakeholder_brief_writer.llm import enrich_brief
        brief = generate_brief(REPORT_TEXT)
        original_summary = brief.narrative_summary
        enriched = enrich_brief(brief, llm_enabled=False)
        assert enriched.narrative_summary == original_summary
        assert enriched.llm_enriched is False

    def test_llm_failure_graceful(self):
        from stakeholder_brief_writer.llm import enrich_brief
        brief = generate_brief(REPORT_TEXT)
        # Use a clearly invalid model to trigger failure path
        enriched = enrich_brief(brief, model="invalid/model-xyz", llm_enabled=True)
        # Should not raise — returns brief intact
        assert isinstance(enriched, ExecutiveBrief)


# ── Model tests ─────────────────────────────────────────────────────────────

class TestModels:
    def test_finding_defaults(self):
        f = ResearchFinding(statement="Test", evidence="")
        assert f.confidence == ConfidenceLevel.MEDIUM
        assert f.impact_scope == ImpactScope.TACTICAL
        assert f.tags == []

    def test_recommendation_defaults(self):
        r = Recommendation(action="Do something", rationale="")
        assert r.priority == 2

    def test_executive_brief_to_dict(self):
        brief = generate_brief(REPORT_TEXT)
        d = brief.to_dict()
        assert isinstance(d, dict)
        assert "top_findings" in d
        assert isinstance(d["top_findings"], list)

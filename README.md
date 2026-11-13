# stakeholder-brief-writer

**CPR Orbital Tool #39 · S6: Pre-study & impact 

Auto-generates a one-page executive summary from a full research report. Built for UX researchers who need to communicate findings to decision-makers — without spending an afternoon reformatting bullet points.

---

## The problem

You've done the research. You have 15 pages of findings, quotes, and recommendations. The VP wants one page by tomorrow. The process of distilling that into a crisp, stakeholder-facing brief is time-consuming, error-prone, and often deprioritised — meaning insights get buried in documents that don't get read.

`stakeholder-brief-writer` automates the extraction and formatting. It identifies findings, recommendations, research questions, limitations, and key metrics from your report — then surfaces them in a clean one-page brief.

---

## Features

- **Automatic section extraction** — detects findings, recommendations, research questions, limitations, and next steps using structural heuristics
- **Confidence & impact tagging** — each finding is automatically tagged with confidence level (high/medium/low) and impact scope (strategic/tactical/operational)
- **Key metric extraction** — pulls participant counts, satisfaction scores, and SUS scores from body text
- **Study type inference** — identifies qualitative, quantitative, and mixed-methods studies from report language
- **LLM enrichment (on by default)** — Claude Opus 4, Gemini 4 Argon, or GPT-5.5 via LiteLLM polish the narrative and refine finding statements; LLM output is additive only and never modifies core extracted data
- **Three export formats** — Markdown one-pager, JSON (structured), plain text (for slides/email)
- **Batch processing** — generate briefs from a directory of reports in one command
- **Rule-based fallback** — works fully offline with zero API calls; LLM backends degrade gracefully

---

## Install

```bash
pip install stakeholder-brief-writer
```

With Streamlit UI:

```bash
pip install stakeholder-brief-writer[ui]
```

---

## Usage

### CLI

```bash
# Generate a brief from a markdown report
stakeholder-brief-writer generate report.md

# Specify output format
stakeholder-brief-writer generate report.md --format all --output ./briefs

# Use a specific LLM backend
stakeholder-brief-writer generate report.md --model gemini/gemini-4-argon

# Rule-based only (no API key needed)
stakeholder-brief-writer generate report.md --no-llm

# Batch process multiple reports
stakeholder-brief-writer batch report1.md report2.md report3.md --output ./briefs
```

### Streamlit UI

```bash
streamlit run stakeholder_brief_writer/app.py
```

### Python API

```python
from stakeholder_brief_writer import generate_brief, to_markdown
from stakeholder_brief_writer.llm import enrich_brief

report = open("research_report.md").read()

# Extract structure (rule-based, no API key)
brief = generate_brief(report)

# Polish with LLM (optional)
brief = enrich_brief(brief, model="anthropic/claude-opus-4-7")

# Export
print(to_markdown(brief))
```

---

## LLM backends

Set environment variables for your chosen provider — the tool tries each in order and falls back to rule-based output if none are available.

```bash
export ANTHROPIC_API_KEY=your_key
export GOOGLE_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

Supported models (LiteLLM format):
- `anthropic/claude-opus-4-7`
- `gemini/gemini-4-argon`
- `openai/gpt-5.5`

---

## Input format

The tool accepts any Markdown or plain-text research report. It works best when the report uses standard section headings:

- `## Key Findings` (or Findings, Results, What we found)
- `## Recommendations` (or Next Steps, Actions)
- `## Research Questions` (or Study Goals, Objectives)
- `## Limitations` (or Caveats, Constraints)
- `## Next Steps` (or Follow-up, Future Work)

Bullet points and numbered lists within each section are extracted automatically.

---

## Output example

```markdown
# Checkout Flow UX Research

**Study type:** Qualitative (interviews)
**Participants:** 12 participants

## Summary
This qualitative study involved 12 participants. The research surfaced 5 key findings
with 4 actionable recommendations, converging on checkout friction as the primary
driver of abandonment.

## Key Findings
1. **68% cited unexpected shipping costs as primary abandonment trigger** [HIGH] [TACTICAL]
2. **Promo code field was consistently missed** [MEDIUM] [TACTICAL]
...

## Recommendations
- **[High]** Move shipping cost estimate to cart page
- **[High]** Reposition promo code field adjacent to order summary
...
```

---

## Limitations

`stakeholder-brief-writer` is an extraction and formatting tool — it does not validate whether findings are methodologically sound. Structural heuristics work well on standard research report formats; heavily non-standard documents may require the `--no-llm` flag and manual review.

**This tool does not replace researcher judgement.** The brief it generates is a starting point for review, not a publishable output without human oversight.

---

## Part of the CPR Ecosystem

`stakeholder-brief-writer` is Tool #39 in the [CPR Orbital series](https://kgkazakos.github.io).

Pairs well with:
- [**evidence-chain**](https://github.com/kgkazakos/evidence-chain) (#23) — tracks claim-to-evidence provenance before you compress it into a brief
- [**insight-differ**](https://github.com/kgkazakos/insight-differ) (#05) — surfaces contradictions between two reports before you synthesise them
- [**affinity-bot**](https://github.com/kgkazakos/affinity-bot) (#34) — clusters raw notes into the themes that become brief findings
- [**jtbd-extractor**](https://github.com/kgkazakos/jtbd-extractor) (#35) — extracts JTBD statements that can anchor brief recommendations

Part of [Computational Product Research](https://kgkazakos.github.io) — an independent discipline for AI-native product research infrastructure.

---

## License

MIT © Kostas Kazakos

"""Basic usage example for stakeholder-brief-writer."""

from stakeholder_brief_writer import generate_brief, to_markdown

SAMPLE_REPORT = """
# Mobile Onboarding Research — Q2 2026

## Research Questions
- Where do users drop off during first-run setup?
- What motivates users to complete profile setup?

## Participants
n=16 participants recruited via screener. Mix of iOS and Android users.

## Key Findings
- 11 of 16 users skipped the profile photo step entirely; they found it premature
- Permission prompts for notifications caused 7 drop-offs in the first session
- Users who completed the tutorial retained at 3x the rate of those who skipped it

## Recommendations
- Move profile photo to day-7 nudge, not onboarding step 2
- Defer notification permission request to post-first-value moment
- Make tutorial skippable but surface a resume prompt on next login

## Limitations
- Sample limited to English-speaking markets
- Lab conditions may not reflect real first-run distraction levels

## Next Steps
- Instrument funnel to capture exact drop-off points quantitatively
- A/B test deferred notification prompt timing
"""

# Rule-based only (no API key needed)
brief = generate_brief(SAMPLE_REPORT)
print(to_markdown(brief))

# With LLM enrichment (requires API key)
# from stakeholder_brief_writer.llm import enrich_brief
# brief = enrich_brief(brief, model="anthropic/claude-opus-4-7")
# print(to_markdown(brief))

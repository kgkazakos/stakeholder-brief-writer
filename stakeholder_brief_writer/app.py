"""Streamlit UI for stakeholder-brief-writer."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from stakeholder_brief_writer.engine import BriefConfig, generate_brief
from stakeholder_brief_writer.export import to_json, to_markdown, to_text
from stakeholder_brief_writer.llm import DEFAULT_MODELS, enrich_brief

st.set_page_config(
    page_title="stakeholder-brief-writer · CPR Orbital #39",
    page_icon="📋",
    layout="wide",
)

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&display=swap');
html, body, [class*="css"] { font-family: 'DM Mono', monospace !important; }

section[data-testid="stSidebar"] {
    background: #111111 !important;
    color: #e8e4dc !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] * { color: #e8e4dc !important; }
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #d94f2a !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

div[data-testid="column"]:first-child .block-container { background: #2b2318 !important; }

.main .block-container {
    background: #f7f4ee !important;
    padding: 1.5rem 2rem !important;
}

.finding-card {
    background: #fff;
    border: 0.5px solid #e0dbd0;
    border-left: 3px solid #d94f2a;
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
}
.rec-card {
    background: #fff;
    border: 0.5px solid #e0dbd0;
    border-left: 3px solid #185fa5;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
}
.badge {
    display: inline-block;
    padding: 1px 7px;
    border-radius: 3px;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    margin-right: 4px;
}
.badge-high { background: #e1f5ee; color: #0f6e56; border: 0.5px solid #a3d9c4; }
.badge-medium { background: #faeeda; color: #854f0b; border: 0.5px solid #f5c77a; }
.badge-low { background: #fde8e4; color: #993c1d; border: 0.5px solid #f5b4a8; }
.badge-strategic { background: #e6f1fb; color: #185fa5; border: 0.5px solid #b5d4f4; }
.badge-tactical { background: #f1efe8; color: #5f5e5a; border: 0.5px solid #d3d1c7; }
.badge-operational { background: #f5f5f5; color: #555; border: 0.5px solid #ddd; }
.meta-line {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #999;
    margin-top: 4px;
}
.summary-box {
    background: #fff;
    border: 0.5px solid #e0dbd0;
    border-radius: 6px;
    padding: 14px 16px;
    font-size: 12px;
    line-height: 1.65;
    margin-bottom: 16px;
}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### CPR Orbital")
    st.markdown("**#39** stakeholder-brief-writer")
    st.markdown("---")
    st.markdown("### Settings")

    llm_on = st.toggle("LLM enrichment", value=True)
    model_choice = st.selectbox(
        "Model",
        DEFAULT_MODELS,
        index=1,
        disabled=not llm_on,
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("### Extract")
    max_findings = st.slider("Max findings", 2, 8, 5)
    max_recs = st.slider("Max recommendations", 1, 6, 4)
    st.markdown("---")
    st.markdown("### Export")
    export_fmt = st.radio("Format", ["Markdown", "JSON", "Text"], index=0)
    st.markdown("---")
    st.markdown(
        '<span style="font-size:10px;color:#555">Tool 39 of 40 · CPR Orbital<br>kgkazakos.github.io</span>',
        unsafe_allow_html=True,
    )

# ── MAIN ───────────────────────────────────────────────────────────────────
st.markdown(
    "## stakeholder-brief-writer",
    help="Auto-generates a one-page executive summary from a full research report.",
)
st.markdown(
    '<span style="font-size:12px;color:#888">CPR Orbital #39 · One-page executive summaries from research reports</span>',
    unsafe_allow_html=True,
)

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("**Research Report**")
    report_text = st.text_area(
        "Paste your full research report (Markdown or plain text)",
        height=340,
        placeholder="# Checkout Flow Research\n\n## Research Questions\n- Why do users abandon checkout?\n\n## Key Findings\n- 68% of users cited unexpected shipping costs as the primary abandonment trigger\n- ...",
        label_visibility="collapsed",
    )
    run_btn = st.button("Generate Brief", type="primary", use_container_width=True)

with col_output:
    if run_btn and report_text.strip():
        config = BriefConfig(max_findings=max_findings, max_recommendations=max_recs)
        with st.spinner("Extracting structure…"):
            brief = generate_brief(report_text, config)
        if llm_on:
            with st.spinner(f"Enriching via {model_choice}…"):
                brief = enrich_brief(brief, model=model_choice, llm_enabled=True)

        st.session_state["brief"] = brief

    if "brief" in st.session_state:
        brief = st.session_state["brief"]

        st.markdown(f"**{brief.title}**")
        st.markdown(
            f'<div class="meta-line">{brief.study_type} · {brief.participant_summary}'
            + (f' · {" · ".join(f"{k}: {v}" for k, v in brief.key_metrics.items())}' if brief.key_metrics else "")
            + "</div>",
            unsafe_allow_html=True,
        )

        if brief.narrative_summary:
            st.markdown(
                f'<div class="summary-box">{brief.narrative_summary}</div>',
                unsafe_allow_html=True,
            )

        # Findings
        st.markdown("**Key Findings**")
        for i, f in enumerate(brief.top_findings, 1):
            conf_cls = f"badge-{f.confidence.value}"
            scope_cls = f"badge-{f.impact_scope.value}"
            tags_html = "".join(
                f'<span class="badge" style="background:#f5f5f5;color:#888;border:0.5px solid #ddd">{t}</span>'
                for t in f.tags
            )
            evidence_html = f'<div class="meta-line">Evidence: {f.evidence}</div>' if f.evidence else ""
            st.markdown(
                f"""<div class="finding-card">
<span style="font-weight:600;font-size:12px">{i}. {f.statement}</span>
<div style="margin-top:5px">
<span class="badge {conf_cls}">{f.confidence.value}</span>
<span class="badge {scope_cls}">{f.impact_scope.value}</span>
{tags_html}
</div>
{evidence_html}
</div>""",
                unsafe_allow_html=True,
            )

        # Recommendations
        if brief.recommendations:
            st.markdown("**Recommendations**")
            priority_map = {1: ("HIGH", "badge-low"), 2: ("MED", "badge-medium"), 3: ("LOW", "badge-high")}
            for r in brief.recommendations:
                label, cls = priority_map.get(r.priority, ("MED", "badge-medium"))
                owner_html = f'<div class="meta-line">Owner: {r.owner_hint}</div>' if r.owner_hint else ""
                st.markdown(
                    f"""<div class="rec-card">
<span class="badge {cls}">{label}</span> {r.action}
{owner_html}
</div>""",
                    unsafe_allow_html=True,
                )

        # Next steps
        if brief.next_steps:
            st.markdown("**Next Steps**")
            for ns in brief.next_steps:
                st.markdown(f"- {ns}")

        st.divider()
        # Export
        enrichment_note = (
            f"✓ LLM enriched ({brief.llm_model})" if brief.llm_enriched else "rule-based"
        )
        st.caption(f"{enrichment_note} · ~{brief.word_count} words")

        from stakeholder_brief_writer.export import to_json, to_markdown, to_text

        if export_fmt == "Markdown":
            st.download_button(
                "Download Brief (.md)",
                to_markdown(brief),
                file_name="executive_brief.md",
                mime="text/markdown",
            )
        elif export_fmt == "JSON":
            st.download_button(
                "Download Brief (.json)",
                to_json(brief),
                file_name="executive_brief.json",
                mime="application/json",
            )
        else:
            st.download_button(
                "Download Brief (.txt)",
                to_text(brief),
                file_name="executive_brief.txt",
                mime="text/plain",
            )
    elif run_btn:
        st.warning("Paste a research report first.")

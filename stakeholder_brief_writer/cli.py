"""Click CLI for stakeholder-brief-writer."""

from __future__ import annotations

from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .engine import BriefConfig, generate_brief
from .export import to_json, to_markdown, to_text
from .llm import DEFAULT_MODELS, enrich_brief
from .models import ConfidenceLevel

console = Console()


def _priority_label(p: int) -> str:
    return {1: "[bold red]HIGH[/bold red]", 2: "[yellow]MED[/yellow]", 3: "[green]LOW[/green]"}.get(
        p, "MED"
    )


def _conf_colour(c: ConfidenceLevel) -> str:
    return {
        ConfidenceLevel.HIGH: "green",
        ConfidenceLevel.MEDIUM: "yellow",
        ConfidenceLevel.LOW: "red",
    }.get(c, "white")


@click.group()
@click.version_option(package_name="stakeholder-brief-writer")
def cli():
    """stakeholder-brief-writer — one-page executive summaries from research reports.

    Part of the CPR Orbital series · kgkazakos.github.io
    """


@cli.command()
@click.argument("report", type=click.Path(exists=True))
@click.option("--output", "-o", default=".", help="Output directory.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["markdown", "json", "text", "all"]),
    default="markdown",
    show_default=True,
)
@click.option("--max-findings", default=5, show_default=True)
@click.option("--max-recs", default=4, show_default=True)
@click.option(
    "--model",
    default=DEFAULT_MODELS[0],
    show_default=True,
    help="LLM model string (LiteLLM format).",
)
@click.option("--no-llm", is_flag=True, help="Disable LLM enrichment.")
def generate(report, output, fmt, max_findings, max_recs, model, no_llm):
    """Generate a one-page executive brief from REPORT (markdown or text file)."""
    text = Path(report).read_text(encoding="utf-8")
    config = BriefConfig(max_findings=max_findings, max_recommendations=max_recs)

    with console.status("[bold]Extracting structure…"):
        brief = generate_brief(text, config)

    if not no_llm:
        with console.status(f"[bold]Enriching with {model}…"):
            brief = enrich_brief(brief, model=model, llm_enabled=True)

    # Display summary
    console.print(
        Panel(
            f"[bold]{brief.title}[/bold]\n"
            f"[dim]{brief.study_type} · {brief.participant_summary}[/dim]",
            title="[bold orange1]stakeholder-brief-writer[/bold orange1]",
            border_style="orange1",
        )
    )

    if brief.narrative_summary:
        console.print(Panel(brief.narrative_summary, title="Summary", border_style="dim"))

    # Findings table
    t = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    t.add_column("#", width=3)
    t.add_column("Finding")
    t.add_column("Confidence", width=10)
    t.add_column("Scope", width=12)
    for i, f in enumerate(brief.top_findings, 1):
        col = _conf_colour(f.confidence)
        t.add_row(
            str(i),
            f.statement[:90] + ("…" if len(f.statement) > 90 else ""),
            f"[{col}]{f.confidence.value}[/{col}]",
            f.impact_scope.value,
        )
    console.print(t)

    # Recommendations
    if brief.recommendations:
        console.print("[bold]Recommendations:[/bold]")
        for r in brief.recommendations:
            console.print(f"  {_priority_label(r.priority)} {r.action}")

    # Write output
    out_dir = Path(output)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(report).stem

    if fmt in ("markdown", "all"):
        p = out_dir / f"{stem}_brief.md"
        to_markdown(brief, p)
        console.print(f"[green]✓[/green] Markdown → {p}")
    if fmt in ("json", "all"):
        p = out_dir / f"{stem}_brief.json"
        to_json(brief, p)
        console.print(f"[green]✓[/green] JSON → {p}")
    if fmt in ("text", "all"):
        p = out_dir / f"{stem}_brief.txt"
        to_text(brief, p)
        console.print(f"[green]✓[/green] Text → {p}")

    enriched = f"[green]✓ LLM ({brief.llm_model})[/green]" if brief.llm_enriched else "[dim]rule-based[/dim]"
    console.print(f"\nEnrichment: {enriched}  ·  ~{brief.word_count} words")


@cli.command()
@click.argument("reports", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output", "-o", default="briefs", help="Output directory.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["markdown", "json", "text", "all"]),
    default="markdown",
)
@click.option(
    "--model",
    default=DEFAULT_MODELS[0],
    show_default=True,
)
@click.option("--no-llm", is_flag=True)
def batch(reports, output, fmt, model, no_llm):
    """Process multiple REPORTS and write briefs to OUTPUT directory."""
    out_dir = Path(output)
    out_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    for report in reports:
        try:
            text = Path(report).read_text(encoding="utf-8")
            brief = generate_brief(text)
            if not no_llm:
                brief = enrich_brief(brief, model=model, llm_enabled=True)
            stem = Path(report).stem
            if fmt in ("markdown", "all"):
                to_markdown(brief, out_dir / f"{stem}_brief.md")
            if fmt in ("json", "all"):
                to_json(brief, out_dir / f"{stem}_brief.json")
            if fmt in ("text", "all"):
                to_text(brief, out_dir / f"{stem}_brief.txt")
            console.print(f"[green]✓[/green] {report}")
            success += 1
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]✗[/red] {report}: {exc}")

    console.print(f"\n[bold]{success}/{len(reports)}[/bold] reports processed → {out_dir}")


if __name__ == "__main__":
    cli()

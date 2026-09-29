"""
Report generator: takes EvalSummary and produces markdown + JSON output.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .eval_runner import EvalSummary, EvalResult, CategoryScore


def generate_markdown_report(summary: EvalSummary) -> str:
    """Generate a complete markdown evaluation report."""
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Header
    lines.append("# Web-Scraping Skill — Weakness Evaluation Report")
    lines.append("")
    lines.append(f"**Generated**: {now}")
    lines.append(f"**Skill Directory**: `{summary.skill_dir}`")
    lines.append(f"**Files Scanned**: {summary.files_scanned}")
    lines.append(f"**Weaknesses Evaluated**: {summary.total_weaknesses}")
    lines.append("")

    # Overall Score
    lines.append("---")
    lines.append("")
    lines.append("## Overall Score")
    lines.append("")
    lines.append(
        f"### {summary.total_score} / {summary.total_max_score} "
        f"({summary.percentage:.0f}%) — Grade: {summary.grade}"
    )
    lines.append("")

    # Score interpretation
    lines.append(_score_interpretation(summary))
    lines.append("")

    # Category Scores Table
    lines.append("---")
    lines.append("")
    lines.append("## Category Scores")
    lines.append("")
    lines.append("| Category | Score | Max | % | Weaknesses |")
    lines.append("|----------|-------|-----|---|------------|")
    for cat in summary.category_scores:
        bar = _progress_bar(cat.percentage)
        lines.append(
            f"| {cat.category} | {cat.score} | {cat.max_score} | "
            f"{bar} {cat.percentage:.0f}% | {cat.weakness_count} |"
        )
    lines.append("")

    # Detailed Results
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")

    # Group by category
    for cat in summary.category_scores:
        lines.append(f"### {cat.category}")
        lines.append("")

        for result in cat.results:
            icon = _score_icon(result.score)
            lines.append(f"#### {icon} {result.weakness_id}: {result.title}")
            lines.append("")
            lines.append(f"**Score**: {result.score}/{result.max_score}")
            if result.rubric_match:
                lines.append(f"**Rubric Match**: {result.rubric_match}")
            lines.append("")

            # Evidence
            lines.append("**Evidence**:")
            lines.append("")
            if result.evidence:
                for ev in result.evidence[:10]:  # Cap at 10 evidence items
                    lines.append(f"- {ev}")
            else:
                lines.append("- No evidence collected")
            lines.append("")

            # Recommendation (only if score < 3)
            if result.score < MAX_SCORE and result.recommendation:
                lines.append(f"> **Recommendation**: {result.recommendation}")
                lines.append("")
                if result.fix_locations:
                    lines.append(
                        f"> **Fix in**: {', '.join(f'`{loc}`' for loc in result.fix_locations)}"
                    )
                    lines.append("")

        lines.append("---")
        lines.append("")

    # Priority Fix List
    lines.append("## Priority Fix List")
    lines.append("")
    lines.append("Weaknesses ranked by severity (lowest score first):")
    lines.append("")

    sorted_results = sorted(summary.results, key=lambda r: (r.score, r.weakness_id))
    lines.append("| Priority | ID | Title | Score | Category |")
    lines.append("|----------|-----|-------|-------|----------|")
    for i, result in enumerate(sorted_results, 1):
        if result.score >= MAX_SCORE:
            continue  # Don't list already-passing weaknesses
        icon = _score_icon(result.score)
        lines.append(
            f"| {i} | {result.weakness_id} | {icon} {result.title} | "
            f"{result.score}/{result.max_score} | {result.category} |"
        )
    lines.append("")

    # Summary stats
    critical = sum(1 for r in summary.results if r.score == 0)
    partial = sum(1 for r in summary.results if r.score == 1)
    adequate = sum(1 for r in summary.results if r.score == 2)
    excellent = sum(1 for r in summary.results if r.score == 3)

    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"- 🔴 **Critical gaps** (score 0): {critical}")
    lines.append(f"- 🟡 **Partial coverage** (score 1): {partial}")
    lines.append(f"- 🟢 **Adequate coverage** (score 2): {adequate}")
    lines.append(f"- ⭐ **Excellent coverage** (score 3): {excellent}")
    lines.append("")

    return "\n".join(lines)


# Max score constant imported from eval_cases via runner
MAX_SCORE = 3


def generate_json_report(summary: EvalSummary) -> dict:
    """Generate a machine-readable JSON report for tracking."""
    now = datetime.now(timezone.utc).isoformat()

    return {
        "metadata": {
            "generated_at": now,
            "skill_dir": summary.skill_dir,
            "files_scanned": summary.files_scanned,
            "total_weaknesses": summary.total_weaknesses,
            "eval_version": "1.0.0",
        },
        "overall": {
            "score": summary.total_score,
            "max_score": summary.total_max_score,
            "percentage": round(summary.percentage, 1),
            "grade": summary.grade,
        },
        "categories": [
            {
                "name": cat.category,
                "score": cat.score,
                "max_score": cat.max_score,
                "percentage": round(cat.percentage, 1),
                "weakness_count": cat.weakness_count,
            }
            for cat in summary.category_scores
        ],
        "weaknesses": [
            {
                "id": r.weakness_id,
                "category": r.category,
                "title": r.title,
                "score": r.score,
                "max_score": r.max_score,
                "rubric_match": r.rubric_match,
                "evidence_count": len(r.evidence),
                "evidence": r.evidence[:5],  # Top 5 for JSON brevity
                "recommendation": r.recommendation,
                "fix_locations": r.fix_locations,
            }
            for r in summary.results
        ],
        "priority_fixes": [
            {
                "priority": i + 1,
                "id": r.weakness_id,
                "title": r.title,
                "score": r.score,
                "category": r.category,
            }
            for i, r in enumerate(
                sorted(
                    [r for r in summary.results if r.score < MAX_SCORE],
                    key=lambda r: (r.score, r.weakness_id),
                )
            )
        ],
    }


def write_reports(
    summary: EvalSummary,
    output_dir: str,
    formats: str = "both",
) -> list[str]:
    """
    Write evaluation reports to disk.

    Args:
        summary: The eval results.
        output_dir: Directory to write reports to.
        formats: "md", "json", or "both".

    Returns:
        List of file paths written.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    if formats in ("md", "both"):
        md_path = out / "eval_report.md"
        md_content = generate_markdown_report(summary)
        md_path.write_text(md_content, encoding="utf-8")
        written.append(str(md_path))

    if formats in ("json", "both"):
        json_path = out / "eval_scores.json"
        json_data = generate_json_report(summary)
        json_path.write_text(
            json.dumps(json_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        written.append(str(json_path))

    return written


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _score_icon(score: int) -> str:
    """Return an icon for a given score."""
    if score == 0:
        return "🔴"
    elif score == 1:
        return "🟡"
    elif score == 2:
        return "🟢"
    else:
        return "⭐"


def _progress_bar(percentage: float, width: int = 10) -> str:
    """Generate a text progress bar."""
    filled = int(percentage / 100 * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"


def _score_interpretation(summary: EvalSummary) -> str:
    """Return a human-readable interpretation of the overall score."""
    pct = summary.percentage
    if pct >= 90:
        return (
            "The skill has excellent coverage across all weakness categories. "
            "Only minor polish items remain."
        )
    elif pct >= 75:
        return (
            "The skill has good overall coverage with a few notable gaps. "
            "The recommendations below would bring it to production-grade completeness."
        )
    elif pct >= 50:
        return (
            "The skill has meaningful gaps in several categories. "
            "Addressing the priority fixes below would significantly improve reliability."
        )
    elif pct >= 25:
        return (
            "The skill has significant gaps across multiple categories. "
            "The core architecture may be sound, but content coverage needs substantial work."
        )
    else:
        return (
            "The skill has critical gaps in most categories. "
            "A comprehensive content review and expansion is recommended."
        )

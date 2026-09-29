import argparse
import sys
from pathlib import Path

from .eval_runner import SkillEvalRunner
from .eval_report import write_reports


def main():
    parser = argparse.ArgumentParser(description="Evaluate web-scraping skill weaknesses")
    parser.add_argument(
        "--skill-dir",
        type=str,
        default="..",
        help="Path to the web-scraping skill directory (default: ..)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Directory to save the evaluation reports (default: results)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["md", "json", "both"],
        default="both",
        help="Output format: md, json, or both (default: both)",
    )

    args = parser.parse_args()

    skill_path = Path(args.skill_dir).resolve()
    if not skill_path.exists():
        print(f"Error: Skill directory not found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning skill files in: {skill_path}")
    runner = SkillEvalRunner(skill_dir=str(skill_path))
    summary = runner.run()

    print(f"Evaluated {summary.total_weaknesses} weaknesses across {summary.files_scanned} files.")
    print(f"Overall Score: {summary.total_score}/{summary.total_max_score} ({summary.percentage:.1f}%)")

    output_path = Path(args.output_dir).resolve()
    written_files = write_reports(summary, output_dir=str(output_path), formats=args.format)

    print("\nReports written to:")
    for f in written_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()

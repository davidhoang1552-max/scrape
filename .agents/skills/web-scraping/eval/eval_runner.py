"""
Main eval engine: scans skill files, runs pattern matching against each
weakness test case, and produces scored results.
"""

import glob
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .eval_cases import (
    ALL_CASES,
    CASES_BY_ID,
    CATEGORIES,
    MAX_SCORE_PER_WEAKNESS,
    TOTAL_MAX_SCORE,
    EvalCase,
)


@dataclass
class EvalResult:
    """Result of evaluating a single weakness."""
    weakness_id: str
    category: str
    title: str
    score: int  # 0-3
    max_score: int  # Always 3
    evidence: list[str] = field(default_factory=list)  # What was found (or not)
    recommendation: str = ""
    fix_locations: list[str] = field(default_factory=list)
    rubric_match: str = ""  # Which rubric level this maps to


@dataclass
class CategoryScore:
    """Aggregated score for a category."""
    category: str
    score: int
    max_score: int
    weakness_count: int
    results: list[EvalResult] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return (self.score / self.max_score * 100) if self.max_score > 0 else 0.0


@dataclass
class EvalSummary:
    """Overall eval results."""
    total_score: int
    total_max_score: int
    category_scores: list[CategoryScore]
    results: list[EvalResult]
    skill_dir: str
    files_scanned: int
    total_weaknesses: int

    @property
    def percentage(self) -> float:
        return (self.total_score / self.total_max_score * 100) if self.total_max_score > 0 else 0.0

    @property
    def grade(self) -> str:
        pct = self.percentage
        if pct >= 90:
            return "A"
        elif pct >= 80:
            return "B"
        elif pct >= 70:
            return "C"
        elif pct >= 60:
            return "D"
        else:
            return "F"


class SkillEvalRunner:
    """
    Evaluates a web-scraping skill directory against the weakness rubric.

    Usage:
        runner = SkillEvalRunner(skill_dir="path/to/web-scraping")
        summary = runner.run()
    """

    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir).resolve()
        self._file_cache: dict[str, str] = {}  # path -> contents
        self._files_scanned: set[str] = set()

    def run(self) -> EvalSummary:
        """Run all eval cases and return aggregated results."""
        results: list[EvalResult] = []
        for case in ALL_CASES:
            result = self._eval_case(case)
            results.append(result)

        # Aggregate by category
        category_scores = self._aggregate_categories(results)

        total_score = sum(r.score for r in results)

        return EvalSummary(
            total_score=total_score,
            total_max_score=TOTAL_MAX_SCORE,
            category_scores=category_scores,
            results=results,
            skill_dir=str(self.skill_dir),
            files_scanned=len(self._files_scanned),
            total_weaknesses=len(ALL_CASES),
        )

    def _eval_case(self, case: EvalCase) -> EvalResult:
        """Evaluate a single weakness test case."""
        # Resolve target files to actual paths
        target_files = self._resolve_files(case.target_files)
        evidence: list[str] = []
        positive_hits = 0
        negative_hits = 0
        total_positive_patterns = len(case.search_patterns)

        # Scan each target file
        for filepath in target_files:
            content = self._read_file(filepath)
            if content is None:
                evidence.append(f"⚠ File not found: {os.path.basename(filepath)}")
                continue

            self._files_scanned.add(filepath)
            relpath = os.path.relpath(filepath, self.skill_dir)

            # Check positive patterns (presence = good)
            for pattern in case.search_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    positive_hits += 1
                    # Find the line for context
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            snippet = line.strip()[:100]
                            evidence.append(
                                f"✓ [{relpath}:{line_num}] Pattern `{pattern}` → \"{snippet}\""
                            )
                            break  # Only report first match per pattern per file

            # Check negative patterns (presence = bad)
            for pattern in case.negative_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    negative_hits += 1
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            snippet = line.strip()[:100]
                            evidence.append(
                                f"✗ [{relpath}:{line_num}] Anti-pattern `{pattern}` → \"{snippet}\""
                            )
                            break

        # Score based on positive/negative pattern coverage
        score = self._compute_score(
            case, positive_hits, total_positive_patterns, negative_hits, target_files
        )

        # Map to rubric description
        rubric_match = self._get_rubric_description(case, score)

        if not evidence:
            evidence.append(f"✗ No matches found in {len(target_files)} scanned file(s)")

        return EvalResult(
            weakness_id=case.weakness_id,
            category=case.category,
            title=case.title,
            score=score,
            max_score=MAX_SCORE_PER_WEAKNESS,
            evidence=evidence,
            recommendation=case.recommendation,
            fix_locations=case.fix_locations,
            rubric_match=rubric_match,
        )

    def _compute_score(
        self,
        case: EvalCase,
        positive_hits: int,
        total_positive_patterns: int,
        negative_hits: int,
        target_files: list[str],
    ) -> int:
        """
        Compute score (0-3) based on pattern matching results.

        Scoring logic:
        - Base score from positive pattern coverage ratio
        - Penalty for negative pattern hits
        - Bonus for file existence (when checking for new files like CHANGELOG.md)
        """
        if total_positive_patterns == 0:
            # No patterns to check — score based on negative patterns only
            if negative_hits > 0:
                return 0
            return 2  # Neutral — can't evaluate

        # Coverage ratio: how many unique patterns found across all files
        coverage = positive_hits / total_positive_patterns

        # Base score from coverage (thresholds tuned to prevent ceiling effect —
        # 40% superficial matches should NOT earn a perfect score)
        if coverage == 0:
            base_score = 0
        elif coverage < 0.10:
            base_score = 1
        elif coverage < 0.80:
            base_score = 2
        else:
            base_score = 3

        # Penalty for negative patterns
        if negative_hits > 0:
            base_score = max(0, base_score - negative_hits)

        # Handle file-not-found case (e.g., checking for CHANGELOG.md)
        missing_files = [f for f in target_files if self._read_file(f) is None]
        critical_missing = [
            f for f in missing_files
            if os.path.basename(f) in ("CHANGELOG.md",)
        ]
        if critical_missing and base_score > 1:
            base_score = min(base_score, 1)

        return min(base_score, MAX_SCORE_PER_WEAKNESS)

    def _get_rubric_description(self, case: EvalCase, score: int) -> str:
        """Get the rubric description for a given score."""
        if case.scoring_rubric is None:
            return ""
        mapping = {
            0: case.scoring_rubric.score_0,
            1: case.scoring_rubric.score_1,
            2: case.scoring_rubric.score_2,
            3: case.scoring_rubric.score_3,
        }
        return mapping.get(score, "")

    def _resolve_files(self, patterns: list[str]) -> list[str]:
        """Resolve glob patterns to actual file paths relative to skill_dir."""
        resolved = []
        for pattern in patterns:
            # Handle relative patterns (../ for multi-tiered-scraping)
            if pattern.startswith("../"):
                base = self.skill_dir.parent
                pattern = pattern[3:]
            else:
                base = self.skill_dir

            full_pattern = str(base / pattern)

            # Use glob to expand
            matches = glob.glob(full_pattern, recursive=True)
            if matches:
                resolved.extend(matches)
            else:
                # If no glob match, treat as literal path
                literal = str(base / pattern)
                resolved.append(literal)

        # Exclude ALL results directories (eval/results/ and results/)
        # which contain keywords from previous runs, inflating scores.
        eval_results_dir = str((self.skill_dir / "eval" / "results").resolve())
        root_results_dir = str((self.skill_dir / "results").resolve())
        resolved = [
            f for f in resolved
            if not str(Path(f).resolve()).startswith(eval_results_dir)
            and not str(Path(f).resolve()).startswith(root_results_dir)
        ]

        return list(set(resolved))  # Deduplicate

    def _read_file(self, filepath: str) -> Optional[str]:
        """Read and cache a file's contents. Returns None if file doesn't exist."""
        filepath = str(Path(filepath).resolve())
        if filepath in self._file_cache:
            return self._file_cache[filepath]
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self._file_cache[filepath] = content
            return content
        except (FileNotFoundError, PermissionError, IsADirectoryError):
            self._file_cache[filepath] = None
            return None

    def _aggregate_categories(self, results: list[EvalResult]) -> list[CategoryScore]:
        """Group results by category and compute category scores."""
        cat_map: dict[str, list[EvalResult]] = {}
        for r in results:
            cat_map.setdefault(r.category, []).append(r)

        scores = []
        for cat in CATEGORIES:
            cat_results = cat_map.get(cat, [])
            cat_score = sum(r.score for r in cat_results)
            cat_max = sum(r.max_score for r in cat_results)
            scores.append(
                CategoryScore(
                    category=cat,
                    score=cat_score,
                    max_score=cat_max,
                    weakness_count=len(cat_results),
                    results=cat_results,
                )
            )
        return scores

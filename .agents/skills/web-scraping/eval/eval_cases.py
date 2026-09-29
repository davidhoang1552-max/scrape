"""
Eval test case definitions for 16 identified weaknesses across 6 categories.

Each weakness is a structured test case with:
- search_patterns: regex patterns to look for (presence = good)
- negative_patterns: regex patterns that indicate the weakness (presence = bad)
- target_files: which files to scan (glob patterns relative to skill root)
- scoring_rubric: what constitutes 0/1/2/3
- recommendation: what to fix and where

Weaknesses W1-W12 come from content gap analysis.
Weaknesses W13-W16 come from the external engineering evaluation (9.2/10 rated).
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ScoringRubric:
    """Defines what score each evidence level produces."""
    score_0: str  # Critical gap — what absence looks like
    score_1: str  # Partial — minimal mention only
    score_2: str  # Adequate — reasonable coverage but not comprehensive
    score_3: str  # Excellent — thorough, actionable coverage


@dataclass
class EvalCase:
    """A single weakness test case."""
    weakness_id: str
    category: str
    title: str
    description: str
    evidence_summary: str  # Brief summary of why this is a weakness
    search_patterns: List[str]  # Regex patterns — presence indicates coverage (good)
    negative_patterns: List[str] = field(default_factory=list)  # Presence indicates the weakness (bad)
    target_files: List[str] = field(default_factory=lambda: ["**/*.md"])  # Glob patterns
    scoring_rubric: Optional[ScoringRubric] = None
    recommendation: str = ""
    fix_locations: List[str] = field(default_factory=list)  # Specific files to modify


# ---------------------------------------------------------------------------
# Category 1: Error Handling & Resilience
# ---------------------------------------------------------------------------

W1 = EvalCase(
    weakness_id="W1",
    category="Error Handling & Resilience",
    title="No timeout/retry guidance for proxy-mcp tools",
    description=(
        "Reconnaissance workflow calls proxy_list_traffic(), proxy_get_exchange() etc. "
        "with no timeout, retry, or failure handling patterns. If the MITM proxy hangs "
        "or a tool call fails, the agent has no recovery path."
    ),
    evidence_summary=(
        "All proxy-mcp tool invocations across workflows/ and strategies/ lack any "
        "nearby timeout, retry, or error handling guidance."
    ),
    search_patterns=[
        r"timeout",
        r"retry",
        r"fallback.*proxy",
        r"proxy.*fail",
        r"tool.*fail",
        r"MCP.*unavailable",
        r"error.*handling.*proxy",
        r"try.*again",
        r"max.*attempts",
    ],
    target_files=[
        "workflows/reconnaissance.md",
        "strategies/traffic-interception.md",
        "strategies/session-workflows.md",
        "reference/proxy-tool-reference.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No mention of timeout, retry, or error handling near proxy-mcp tool calls",
        score_1="Mentions 'retry' or 'timeout' once in passing, no actionable pattern",
        score_2="Has a general error handling section but not specific to proxy-mcp tools",
        score_3="Provides explicit timeout/retry patterns for proxy-mcp tools with example code",
    ),
    recommendation=(
        "Add a 'Tool Error Handling' subsection to workflows/reconnaissance.md that covers: "
        "(1) What to do when proxy_start() fails, (2) timeout patterns for tool calls, "
        "(3) retry logic for flaky MCP connections, (4) graceful degradation to curl-only "
        "reconnaissance when MCP is unavailable."
    ),
    fix_locations=[
        "workflows/reconnaissance.md",
        "reference/proxy-tool-reference.md",
    ],
)

W2 = EvalCase(
    weakness_id="W2",
    category="Error Handling & Resilience",
    title="No graceful degradation when proxy-mcp is unavailable",
    description=(
        "SKILL.md Phases 1-4 assume proxy-mcp is always available. No fallback for "
        "when the MCP server isn't running, tools fail to connect, or the user doesn't "
        "have proxy-mcp installed."
    ),
    evidence_summary=(
        "The entire reconnaissance workflow (Phases 1-4) is completely dependent on "
        "proxy-mcp tools. Phase 0 (curl) is the only phase that works without it."
    ),
    search_patterns=[
        r"without.*proxy.*mcp",
        r"proxy.*mcp.*not.*available",
        r"fallback.*without.*browser",
        r"curl.*only.*mode",
        r"MCP.*not.*installed",
        r"graceful.*degrad",
        r"alternative.*tool",
    ],
    target_files=[
        "SKILL.md",
        "workflows/reconnaissance.md",
        "strategies/traffic-interception.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No mention of proxy-mcp being optional or unavailable",
        score_1="Mentions 'MCP Tools Required' as a prerequisite but no fallback",
        score_2="Acknowledges proxy-mcp may not be available with a brief note",
        score_3="Provides a complete curl-only fallback workflow when proxy-mcp is unavailable",
    ),
    recommendation=(
        "Add a 'Degraded Mode: Without proxy-mcp' section to SKILL.md that maps each "
        "phase to its non-MCP alternative: Phase 0 = curl (already works), Phase 1 = "
        "browser_subagent or manual DevTools, Phase 2 = skip, Phase 3 = manual validation, "
        "Phase 4 = curl + header inspection."
    ),
    fix_locations=["SKILL.md", "workflows/reconnaissance.md"],
)

W3 = EvalCase(
    weakness_id="W3",
    category="Error Handling & Resilience",
    title="Bare except/pass pattern in multi-tiered-scraping code example",
    description=(
        "The multi-tiered-scraping skill's code example uses `except Exception: pass` "
        "which silently swallows all errors during the fast fetch tier. This teaches "
        "agents to write code that hides failures."
    ),
    evidence_summary=(
        "multi-tiered-scraping/SKILL.md lines 52-53 show `except Exception: pass` "
        "as the recommended pattern for handling HTTP errors."
    ),
    search_patterns=[
        r"log.*error",
        r"log.*warning",
        r"logger\.",
        r"raise",
        r"except.*as\s+\w+",
    ],
    negative_patterns=[
        r"except\s*(Exception)?:\s*\n\s*pass",
        r"except:\s*\n\s*pass",
    ],
    target_files=[
        "../multi-tiered-scraping/SKILL.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="Uses bare `except: pass` or `except Exception: pass` in code examples",
        score_1="Catches exceptions but doesn't log or re-raise",
        score_2="Catches specific exceptions and logs them",
        score_3="Catches specific exceptions, logs, and has retry/fallback logic",
    ),
    recommendation=(
        "Replace `except Exception: pass` with `except (httpx.TimeoutException, "
        "httpx.NetworkError) as e: logger.debug(f'Fast fetch failed for {url}: {e}')`. "
        "This preserves the fallback-to-Playwright behavior while making failures visible."
    ),
    fix_locations=["../multi-tiered-scraping/SKILL.md"],
)

# ---------------------------------------------------------------------------
# Category 2: Edge Case Coverage
# ---------------------------------------------------------------------------

W4 = EvalCase(
    weakness_id="W4",
    category="Edge Case Coverage",
    title="No handling for authentication-gated content",
    description=(
        "SKILL.md's Known Major Sites table notes LinkedIn 'requires authentication for "
        "most data' but provides no workflow for handling login flows, cookie-based auth, "
        "or OAuth. The decision tree mentions 'Record auth flow, extract tokens' but no "
        "actual instructions on HOW."
    ),
    evidence_summary=(
        "The decision tree in reconnaissance.md (line ~560) says 'Auth required? → YES → "
        "Record auth flow, extract tokens' but this is a one-liner with zero implementation "
        "guidance."
    ),
    search_patterns=[
        r"login.*flow",
        r"authentication.*workflow",
        r"cookie.*auth",
        r"OAuth",
        r"session.*token",
        r"bearer.*token",
        r"login.*form",
        r"credential.*inject",
        r"auth.*header",
        r"how.*to.*login",
        r"record.*auth.*flow",
    ],
    target_files=[
        "SKILL.md",
        "workflows/reconnaissance.md",
        "strategies/*.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No authentication workflow beyond a one-liner mention",
        score_1="Mentions authentication as a consideration but no steps",
        score_2="Has a basic auth section with cookie/token extraction guidance",
        score_3="Full auth workflow: login recording, token extraction, session reuse, refresh handling",
    ),
    recommendation=(
        "Add strategies/authentication.md covering: (1) Recording login flows via "
        "proxy traffic capture, (2) Extracting session cookies/tokens from browser, "
        "(3) Replaying auth in HTTP clients, (4) Token refresh/rotation patterns, "
        "(5) When to give up (2FA, CAPTCHA-gated login)."
    ),
    fix_locations=["strategies/", "workflows/reconnaissance.md"],
)

W5 = EvalCase(
    weakness_id="W5",
    category="Edge Case Coverage",
    title="No handling for non-English / internationalized sites",
    description=(
        "Framework signatures and examples are English-only. The user's own pipeline.py "
        "shows real Vietnamese scraping, but the skill itself has zero guidance on encoding "
        "issues, i18n URL patterns, non-Latin selectors, or locale-dependent content."
    ),
    evidence_summary=(
        "Zero mentions of UTF-8, encoding, i18n, locale, non-English, CJK, or Unicode "
        "handling in any of the 30+ skill files."
    ),
    search_patterns=[
        r"UTF-?8",
        r"encod",
        r"i18n",
        r"internation",
        r"locale",
        r"non-English",
        r"CJK",
        r"unicode",
        r"charset",
        r"Accept-Language",
        r"lang=",
        r"multi-?lingual",
    ],
    target_files=["**/*.md"],
    scoring_rubric=ScoringRubric(
        score_0="No mention of encoding, i18n, or locale handling",
        score_1="Mentions Accept-Language header in one place",
        score_2="Has encoding and locale guidance but no examples",
        score_3="Comprehensive i18n section with encoding, locale headers, non-Latin selector patterns",
    ),
    recommendation=(
        "Add a section to strategies/cheerio-scraping.md or a new strategies/i18n.md "
        "covering: (1) charset detection (meta tag, HTTP header, BOM), (2) ensuring "
        "UTF-8 output in JSON/CSV, (3) Accept-Language header for locale-dependent content, "
        "(4) URL-encoded vs Unicode paths, (5) CJK/RTL text extraction pitfalls."
    ),
    fix_locations=["strategies/cheerio-scraping.md"],
)

W6 = EvalCase(
    weakness_id="W6",
    category="Edge Case Coverage",
    title="No guidance for JavaScript SPA routing (hash/history API)",
    description=(
        "The Cheerio vs Browser test covers 'JS-rendered content' but doesn't address "
        "SPAs where navigation changes #hash or uses history.pushState() without full "
        "page loads. Proxy traffic capture misses client-side routing."
    ),
    evidence_summary=(
        "SPAs using hash routing (#/) or history.pushState() don't trigger network "
        "requests, so proxy_list_traffic() won't capture navigation events. The skill "
        "has no guidance for this common pattern."
    ),
    search_patterns=[
        r"hash.*rout",
        r"pushState",
        r"history.*API",
        r"SPA.*rout",
        r"client.?side.*rout",
        r"single.?page.*app.*rout",
        r"hash.*bang",
        r"#/",
        r"fragment.*navigation",
    ],
    target_files=[
        "strategies/cheerio-vs-browser-test.md",
        "strategies/dom-scraping.md",
        "strategies/framework-signatures.md",
        "SKILL.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No mention of SPA routing, hash routing, or client-side navigation",
        score_1="Mentions 'SPA' or 'single page application' but not routing specifics",
        score_2="Notes that SPAs need browser rendering, but no routing-specific guidance",
        score_3="Explains hash vs history routing, how to detect it, and extraction strategies",
    ),
    recommendation=(
        "Add a 'SPA Routing Patterns' subsection to strategies/dom-scraping.md covering: "
        "(1) How to detect hash routing vs history API, (2) Why proxy traffic capture "
        "misses client-side navigation, (3) Using interceptor_chrome_devtools_navigate() "
        "with hash URLs, (4) Waiting for route-specific DOM updates after navigation."
    ),
    fix_locations=["strategies/dom-scraping.md", "strategies/cheerio-vs-browser-test.md"],
)

# ---------------------------------------------------------------------------
# Category 3: Data Quality & Validation
# ---------------------------------------------------------------------------

W7 = EvalCase(
    weakness_id="W7",
    category="Data Quality & Validation",
    title="No data schema validation patterns",
    description=(
        "Implementation workflow says 'Validate data quality' but provides no schema "
        "validation patterns (Zod, JSON Schema, type assertions). Only checklist items "
        "like 'All fields populated?'"
    ),
    evidence_summary=(
        "workflows/implementation.md Step 2 has a 'Validation Checklist' with 4 bullet "
        "points but no actual validation code or schema definition."
    ),
    search_patterns=[
        r"[Zz]od",
        r"JSON\s*Schema",
        r"Ajv",
        r"type.*check",
        r"schema.*valid",
        r"assert.*type",
        r"interface\s+\w+",
        r"type\s+\w+\s*=",
        r"\.parse\(",
        r"validate.*schema",
    ],
    target_files=[
        "workflows/implementation.md",
        "examples/*.js",
        "apify/templates/**/*.ts",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No schema validation — only text checklists",
        score_1="Has TypeScript interfaces but no runtime validation",
        score_2="Mentions schema validation as a best practice with one example",
        score_3="Provides runtime schema validation patterns (Zod/Ajv) with code examples",
    ),
    recommendation=(
        "Add a 'Data Validation' section to workflows/implementation.md with: "
        "(1) A Zod schema example for scraped product data, (2) A validation step "
        "in the scrape loop that logs invalid records, (3) Percentage-based quality "
        "threshold (e.g., 'abort if >10% of records fail validation')."
    ),
    fix_locations=["workflows/implementation.md"],
)

W8 = EvalCase(
    weakness_id="W8",
    category="Data Quality & Validation",
    title="No deduplication strategy",
    description=(
        "Sitemap + crawl + API can return duplicate URLs/data. No guidance on dedup "
        "by URL, content hash, or unique field. The user's pipeline.py has `self.visited` "
        "set but the skill docs don't teach this."
    ),
    evidence_summary=(
        "No mentions of deduplication, visited set, content hash, or unique field "
        "checking in any strategy or workflow file."
    ),
    search_patterns=[
        r"dedup",
        r"duplicate",
        r"unique",
        r"visited",
        r"seen",
        r"content.*hash",
        r"Set\(\)",
        r"already.*scraped",
        r"skip.*duplicate",
    ],
    target_files=[
        "workflows/implementation.md",
        "strategies/sitemap-discovery.md",
        "strategies/hybrid-approaches.md",
        "SKILL.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No mention of deduplication or duplicate handling",
        score_1="Mentions 'unique URLs' once but no pattern",
        score_2="Describes URL-based dedup but not content-level dedup",
        score_3="Provides URL dedup + content hash dedup + unique field checking patterns",
    ),
    recommendation=(
        "Add a 'Deduplication' subsection to workflows/implementation.md covering: "
        "(1) URL normalization + visited set, (2) Content hash dedup for similar pages, "
        "(3) Crawlee's built-in RequestQueue dedup, (4) Post-scrape dedup by business key."
    ),
    fix_locations=["workflows/implementation.md", "strategies/hybrid-approaches.md"],
)

W9 = EvalCase(
    weakness_id="W9",
    category="Data Quality & Validation",
    title="No output format guidance beyond JSON",
    description=(
        "All examples output JSON via Dataset.pushData(). No guidance on CSV, JSONL "
        "(streaming), or database storage for large datasets. No mention of memory "
        "constraints when scraping 100k+ items."
    ),
    evidence_summary=(
        "Every code example uses JSON output. No mention of CSV, JSONL, streaming, "
        "database, or memory management for large scrapes."
    ),
    search_patterns=[
        r"CSV",
        r"JSONL",
        r"json.*lines",
        r"stream",
        r"database",
        r"SQLite",
        r"postgres",
        r"large.*dataset",
        r"memory",
        r"100k",
        r"million.*record",
        r"batch.*write",
    ],
    target_files=[
        "workflows/implementation.md",
        "apify/configuration.md",
        "SKILL.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="JSON only — no other output format mentioned",
        score_1="Mentions CSV in passing (e.g., 'export to CSV')",
        score_2="Covers JSON + CSV with code examples, mentions streaming",
        score_3="Comprehensive output section: JSON, CSV, JSONL, DB, streaming, memory management",
    ),
    recommendation=(
        "Add an 'Output Formats' section to workflows/implementation.md covering: "
        "(1) Crawlee Dataset export to CSV/JSON/JSONL, (2) Streaming JSONL for 100k+ "
        "items, (3) Memory-efficient batch writing, (4) When to use a database vs files."
    ),
    fix_locations=["workflows/implementation.md"],
)

# ---------------------------------------------------------------------------
# Category 4: Security & Ethics
# ---------------------------------------------------------------------------

W10 = EvalCase(
    weakness_id="W10",
    category="Security & Ethics",
    title="No PII/sensitive data handling guidance",
    description=(
        "Scraping can inadvertently collect emails, phone numbers, personal data. The "
        "anti-blocking.md has an 'Ethical Considerations' section but it's about "
        "respecting rate limits, not about PII handling, GDPR, or data minimization."
    ),
    evidence_summary=(
        "The only ethics section (anti-blocking.md lines 342-353) covers rate limits "
        "and robots.txt but zero guidance on personal data handling."
    ),
    search_patterns=[
        r"PII",
        r"personal.*data",
        r"GDPR",
        r"CCPA",
        r"data.*privacy",
        r"sensitive.*data",
        r"data.*minimiz",
        r"anonymiz",
        r"redact",
        r"consent",
    ],
    target_files=["**/*.md"],
    scoring_rubric=ScoringRubric(
        score_0="No mention of PII, GDPR, or personal data handling",
        score_1="Mentions 'don't scrape private data' as a bullet point",
        score_2="Has a dedicated PII section with basic guidance",
        score_3="Comprehensive data privacy section: PII detection, GDPR, minimization, redaction",
    ),
    recommendation=(
        "Expand the 'Ethical Considerations' section in strategies/anti-blocking.md or "
        "create a new reference/data-privacy.md covering: (1) PII detection patterns "
        "(email, phone, SSN regex), (2) GDPR/CCPA implications of scraping personal data, "
        "(3) Data minimization (only collect what you need), (4) Redaction patterns for "
        "logs and debug output."
    ),
    fix_locations=["strategies/anti-blocking.md"],
)

W11 = EvalCase(
    weakness_id="W11",
    category="Security & Ethics",
    title="Credential exposure risk in proxy examples",
    description=(
        "Multiple examples show inline credentials like "
        '`proxy_set_upstream("http://user:pass@proxy.apify.com:8000")`. '
        "No guidance on using environment variables or secret management."
    ),
    evidence_summary=(
        "Hardcoded user:pass patterns appear in anti-blocking.md (lines 106, 119), "
        "proxy-escalation.md (line 52), and implementation.md (line 81)."
    ),
    search_patterns=[
        r"env(iron)?.*var",
        r"process\.env",
        r"os\.environ",
        r"\$\{?[A-Z_]+\}?",
        r"secret",
        r"\.env\b",
        r"dotenv",
        r"credential.*manag",
        r"PROXY_URL",
        r"API_KEY",
    ],
    negative_patterns=[
        r"user:pass@",
        r"username:password@",
    ],
    target_files=[
        "strategies/anti-blocking.md",
        "strategies/proxy-escalation.md",
        "workflows/implementation.md",
        "workflows/reconnaissance.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="Inline credentials in examples with no env var guidance",
        score_1="Inline credentials shown but a note says 'use env vars in production'",
        score_2="Examples use env vars, but no explanation of secret management",
        score_3="Examples use env vars, explains .env files, warns against hardcoding",
    ),
    recommendation=(
        "Replace all `user:pass@` patterns in examples with `${PROXY_URL}` or "
        "`process.env.PROXY_URL`. Add a note to strategies/anti-blocking.md: "
        "'Never hardcode proxy credentials. Use environment variables or the "
        "Apify input schema for sensitive configuration.'"
    ),
    fix_locations=[
        "strategies/anti-blocking.md",
        "strategies/proxy-escalation.md",
        "workflows/implementation.md",
    ],
)

# ---------------------------------------------------------------------------
# Category 5: Operational Robustness
# ---------------------------------------------------------------------------

W12 = EvalCase(
    weakness_id="W12",
    category="Operational Robustness",
    title="No monitoring/alerting guidance for production scrapers",
    description=(
        "Productionization workflow covers `apify push` but not monitoring schedules, "
        "failure alerts, data quality drift detection, or cost tracking."
    ),
    evidence_summary=(
        "workflows/productionization.md and apify/deployment.md cover 'deploy' but "
        "not 'operate'. No mention of monitoring, alerting, or scheduled runs."
    ),
    search_patterns=[
        r"monitor",
        r"alert",
        r"schedul",
        r"drift",
        r"cost",
        r"health.*check",
        r"watchdog",
        r"notification",
        r"email.*notif",
        r"Slack.*notif",
        r"cron",
        r"recurring",
    ],
    target_files=[
        "workflows/productionization.md",
        "apify/deployment.md",
        "apify/configuration.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No mention of monitoring, alerting, or scheduled runs",
        score_1="Mentions 'schedule' or 'monitor' once without detail",
        score_2="Has basic scheduling guidance but no alerting or drift detection",
        score_3="Comprehensive ops section: scheduling, alerting, drift detection, cost tracking",
    ),
    recommendation=(
        "Add an 'Operations' section to apify/deployment.md or a new "
        "apify/operations.md covering: (1) Apify scheduling (cron syntax), "
        "(2) Webhook notifications for failures, (3) Data quality assertions "
        "(expected row count, non-null fields), (4) Cost monitoring."
    ),
    fix_locations=["apify/deployment.md"],
)

# ---------------------------------------------------------------------------
# Category 6: Structural Quality (from external engineering evaluation)
# ---------------------------------------------------------------------------

W13 = EvalCase(
    weakness_id="W13",
    category="Structural Quality",
    title="No timeout/budget enforcement for reconnaissance phases",
    description=(
        "The skill has no mechanism to prevent runaway execution. If an agent enters "
        "Phase 2 (Deep Scan) and starts clicking through dozens of page elements, "
        "there is no instruction like 'spend no more than 10 minutes on Phase 2' or "
        "'limit deep scan to 5 interactions.'"
    ),
    evidence_summary=(
        "External engineering evaluation (9.2/10) identified this as the primary "
        "reliability weakness. No phase-level time or interaction budget exists."
    ),
    search_patterns=[
        r"budget",
        r"time.*limit",
        r"max.*minutes",
        r"max.*interactions",
        r"stop.*after",
        r"limit.*phase",
        r"ceiling",
        r"cap\b",
        r"at.*most.*\d+",
        r"no.*more.*than.*\d+",
    ],
    target_files=[
        "SKILL.md",
        "workflows/reconnaissance.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No time or interaction budgets for any phase",
        score_1="Mentions 'don't spend too long' without specifics",
        score_2="Has budgets for one phase but not others",
        score_3="Explicit time/interaction budgets for Phases 1-4 with enforcement instructions",
    ),
    recommendation=(
        "Add phase budgets to SKILL.md's phase descriptions: "
        "'Phase 1: max 5 minutes', 'Phase 2: max 5 interactions per missing data point', "
        "'Phase 4: max 3 escalation levels'. Add a meta-instruction: 'If total "
        "reconnaissance exceeds 15 minutes, stop and report with current findings.'"
    ),
    fix_locations=["SKILL.md", "workflows/reconnaissance.md"],
)

W14 = EvalCase(
    weakness_id="W14",
    category="Structural Quality",
    title="Known Major Sites table is too small",
    description=(
        "The framework-signatures.md Known Major Sites table only lists 6 sites "
        "(Amazon, Shopify, WordPress, Medium, LinkedIn, Wix). High-traffic targets "
        "like eBay, Zillow, Indeed, Airbnb, and others are missing."
    ),
    evidence_summary=(
        "External engineering evaluation noted that the agent falls back to generic "
        "detection for many high-traffic sites, which is slower and less reliable."
    ),
    search_patterns=[
        r"ebay",
        r"zillow",
        r"indeed",
        r"airbnb",
        r"twitter|x\.com",
        r"facebook",
        r"instagram",
        r"yelp",
        r"booking\.com",
        r"walmart",
        r"target\.com",
        r"bestbuy",
        r"etsy",
    ],
    target_files=["strategies/framework-signatures.md"],
    scoring_rubric=ScoringRubric(
        score_0="6 or fewer known sites",
        score_1="7-10 known sites",
        score_2="11-15 known sites with architecture notes",
        score_3="16+ known sites with architecture, data strategy, and protection level",
    ),
    recommendation=(
        "Expand the Known Major Sites table in strategies/framework-signatures.md "
        "with at least 10 more high-traffic domains: eBay, Zillow, Indeed, Airbnb, "
        "Walmart, Target, Best Buy, Etsy, Booking.com, Yelp. Include architecture "
        "type, recommended data strategy, and protection level for each."
    ),
    fix_locations=["strategies/framework-signatures.md"],
)

W15 = EvalCase(
    weakness_id="W15",
    category="Structural Quality",
    title="No versioning or changelog",
    description=(
        "For a skill this large and complex (87 files, ~493 KB), there is no "
        "CHANGELOG.md or version number. If Apify CLI changes template names or "
        "Crawlee updates its API, there's no way to track which parts are current."
    ),
    evidence_summary=(
        "External engineering evaluation identified this as a maintainability risk. "
        "No version number in SKILL.md frontmatter and no CHANGELOG.md file."
    ),
    search_patterns=[
        r"version:",
        r"changelog",
        r"CHANGELOG",
        r"## v\d",
        r"## \d+\.\d+",
        r"last.*updated",
        r"revision",
    ],
    target_files=[
        "SKILL.md",
        "CHANGELOG.md",
    ],
    scoring_rubric=ScoringRubric(
        score_0="No version number and no changelog",
        score_1="Version number in frontmatter but no changelog",
        score_2="Version number + basic changelog with dates",
        score_3="Semantic versioning + detailed changelog with breaking changes noted",
    ),
    recommendation=(
        "Add `version: 1.0.0` to the SKILL.md YAML frontmatter. Create a "
        "CHANGELOG.md with the current state as v1.0.0 and guidance for "
        "updating it when Apify/Crawlee APIs change."
    ),
    fix_locations=["SKILL.md", "CHANGELOG.md"],
)

W16 = EvalCase(
    weakness_id="W16",
    category="Structural Quality",
    title="Duplicate content between SKILL.md and reconnaissance.md",
    description=(
        "SKILL.md describes Phases 0-5 in detail (lines 38-222, ~4,500 tokens). "
        "workflows/reconnaissance.md re-describes much of the same workflow with "
        "expanded examples (674 lines, ~5,000 tokens). An agent that reads both "
        "gets ~2,000 tokens of overlapping content."
    ),
    evidence_summary=(
        "External engineering evaluation measured ~2,000 tokens of overlap between "
        "the two files. SKILL.md should reference the workflow file for details "
        "rather than inlining the phase descriptions."
    ),
    search_patterns=[
        r"See.*workflows/reconnaissance",
        r"see.*reconnaissance\.md.*for.*detail",
        r"refer.*to.*reconnaissance",
    ],
    negative_patterns=[
        # Patterns that indicate inline duplication in SKILL.md
        r"proxy_start\(\)",
        r"interceptor_chrome_launch",
        r"proxy_list_traffic",
        r"humanizer_click",
    ],
    target_files=["SKILL.md"],
    scoring_rubric=ScoringRubric(
        score_0="SKILL.md inlines full tool call examples that duplicate reconnaissance.md",
        score_1="Minor inline examples with most detail deferred to reconnaissance.md",
        score_2="SKILL.md has concise phase summaries with cross-references",
        score_3="Zero duplication — SKILL.md is a pure routing table for phase details",
    ),
    recommendation=(
        "Reduce SKILL.md's Phase 0-5 descriptions to concise summaries (2-3 lines each) "
        "with 'See workflows/reconnaissance.md for full details' cross-references. "
        "Move all proxy-mcp tool call examples to the workflow file."
    ),
    fix_locations=["SKILL.md"],
)


# ---------------------------------------------------------------------------
# All cases, indexed by ID
# ---------------------------------------------------------------------------

ALL_CASES: list[EvalCase] = [
    W1, W2, W3, W4, W5, W6, W7, W8, W9, W10, W11, W12, W13, W14, W15, W16,
]

CASES_BY_ID: dict[str, EvalCase] = {c.weakness_id: c for c in ALL_CASES}

CATEGORIES: list[str] = sorted(set(c.category for c in ALL_CASES))

MAX_SCORE_PER_WEAKNESS = 3
TOTAL_MAX_SCORE = len(ALL_CASES) * MAX_SCORE_PER_WEAKNESS

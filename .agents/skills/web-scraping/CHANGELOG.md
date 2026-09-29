# Changelog

All notable changes to the `web-scraping` agent skill will be documented in this file.

**Last updated**: 2026-08-25
**Revision**: 4

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Tested Dependency Versions

| Dependency | Tested Version | Notes |
|------------|---------------|-------|
| Crawlee | 3.x | CheerioCrawler, PlaywrightCrawler, Dataset APIs |
| Apify SDK | 3.x | Actor.main(), Actor.createProxyConfiguration() |
| Apify CLI | 0.20+ | `apify create`, `apify run`, `apify push` |
| Playwright | 1.40+ | Used by PlaywrightCrawler |
| got-scraping | 4.x | HTTP client with TLS fingerprinting |
| Zod | 3.x | Runtime schema validation in implementation patterns |

> **⚠️ Breaking change risk**: When Crawlee v4 ships, review all `CheerioCrawler`/`PlaywrightCrawler` examples for API compatibility. Update this table and bump the skill version.

## v1.2.0 - 2026-08-25

### Fixed
- **Security**: Removed hardcoded `/home/yms/` path leak from `reference/proxy-tool-reference.md` and `workflows/reconnaissance.md`
- **Eval**: Fixed self-referential scoring bug — eval harness no longer scans its own `eval/results/` output directory
- **Eval**: Resolved path comparison fragility in `_resolve_files` exclusion filter (now uses `.resolve()`)
- **Eval**: Converted bare imports to relative imports across `eval_runner.py`, `eval_report.py`, `run_eval.py`
- **Eval**: Added `eval/__main__.py` to restore `python -m eval` invocation after import refactor
- **Resilience**: Wrapped Playwright fallback in `multi-tiered-scraping/SKILL.md` with `try/except` and `finally` for browser cleanup

### Changed
- **Eval**: Raised score=3 threshold from 60% → 80% coverage to eliminate ceiling effect
- **Ops**: Expanded `apify/deployment.md` monitoring section with webhook payloads, watchdog code, and CU limits
- **Docs**: Rewrote proxy-mcp error handling examples as MCP tool-call pseudocode (was incorrectly using JavaScript `await` syntax)
- **Docs**: Cleaned up SKILL.md cross-reference to reconnaissance.md (removed redundant phrasing)

### Breaking Changes
- `eval/run_eval.py` can no longer be run directly with `python run_eval.py`. Use `python -m eval` or `python -m eval.run_eval` from the skill root directory.

## v1.1.0 - 2026-08-23

### Fixed
- **Security**: Removed hardcoded `user:pass@` credentials from `strategies/traffic-interception.md` (F1)
- **Security**: Added credential warning boxes to all upstream proxy examples (F1, F7)
- **Resilience**: Added circuit breaker pattern to `workflows/implementation.md` Step 3 (F2)
- **Data integrity**: Fixed in-memory accumulation in `examples/iterative-fallback.js` — now streams via `Dataset.pushData()` (F3)
- **Auth**: Added complexity gate to decision tree — aborts on 2FA/CAPTCHA login (F4)
- **Eval**: Tightened scoring thresholds from 40% → 60% for perfect score (F5)
- **Budgets**: Added tool-call-count enforcement to all phase budgets in `SKILL.md` (F6)
- **Proxy**: Defaulted to per-host upstream proxying, marked global as advanced (F7)
- **Ethics**: Added concrete `robots.txt` compliance check with code example (F8)
- **Concurrency**: Added backpressure guidance with `p-limit` to `examples/api-scraper.js` (F10)

## v1.0.0 - 2026-08-19

### Added
- Initial versioning applied to the skill.
- Added strict time and interaction budgets to Phases 0-5 to prevent runaway execution.
- Added "Degraded Mode: Without proxy-mcp" for environments missing the required tools.
- (Further additions tracked as part of the v1.0.0 release process to close content gaps)

### Changed
- Deduplicated Phase 0-5 descriptions in `SKILL.md` by referencing `workflows/reconnaissance.md`.

### Guidelines for Maintainers
When updating this skill (e.g., if Apify or Crawlee APIs change), bump the version in `SKILL.md`'s YAML frontmatter and document the breaking changes or additions here.

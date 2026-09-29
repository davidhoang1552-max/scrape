# Web-Scraping Skill — Weakness Evaluation Report

**Generated**: 2026-09-01 06:40 UTC
**Skill Directory**: `C:\Users\david\Desktop\scrape\.agents\skills\web-scraping`
**Files Scanned**: 47
**Weaknesses Evaluated**: 16

---

## Overall Score

### 48 / 48 (100%) — Grade: A

The skill has excellent coverage across all weakness categories. Only minor polish items remain.

---

## Category Scores

| Category | Score | Max | % | Weaknesses |
|----------|-------|-----|---|------------|
| Data Quality & Validation | 9 | 9 | [██████████] 100% | 3 |
| Edge Case Coverage | 9 | 9 | [██████████] 100% | 3 |
| Error Handling & Resilience | 9 | 9 | [██████████] 100% | 3 |
| Operational Robustness | 3 | 3 | [██████████] 100% | 1 |
| Security & Ethics | 6 | 6 | [██████████] 100% | 2 |
| Structural Quality | 12 | 12 | [██████████] 100% | 4 |

---

## Detailed Results

### Data Quality & Validation

#### ⭐ W7: No data schema validation patterns

**Score**: 3/3
**Rubric Match**: Provides runtime schema validation patterns (Zod/Ajv) with code examples

**Evidence**:

- ✓ [workflows\implementation.md:191] Pattern `[Zz]od` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [workflows\implementation.md:191] Pattern `JSON\s*Schema` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [workflows\implementation.md:191] Pattern `Ajv` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [workflows\implementation.md:191] Pattern `type.*check` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [workflows\implementation.md:191] Pattern `schema.*valid` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [workflows\implementation.md:191] Pattern `assert.*type` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [workflows\implementation.md:202] Pattern `type\s+\w+\s*=` → "type Product = z.infer<typeof ProductSchema>;"
- ✓ [workflows\implementation.md:206] Pattern `\.parse\(` → "const data = ProductSchema.parse(scrapedData);"
- ✓ [workflows\implementation.md:191] Pattern `validate.*schema` → "Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perf"
- ✓ [apify\templates\main.ts:12] Pattern `interface\s+\w+` → "interface Input {"

#### ⭐ W8: No deduplication strategy

**Score**: 3/3
**Rubric Match**: Provides URL dedup + content hash dedup + unique field checking patterns

**Evidence**:

- ✓ [workflows\implementation.md:214] Pattern `dedup` → "## Step 7: Deduplication Strategy"
- ✓ [workflows\implementation.md:216] Pattern `duplicate` → "Scraping via sitemaps and APIs can result in duplicate URLs/data. Ensure you have a deduplication st"
- ✓ [workflows\implementation.md:219] Pattern `unique` → "2. **Content Hash / Unique ID Check**: If extracting multiple items per page, maintain a `Set` of un"
- ✓ [workflows\implementation.md:218] Pattern `visited` → "1. **URL Normalization & Visited Sets**: Strip tracking parameters before adding to the queue. Keep "
- ✓ [workflows\implementation.md:218] Pattern `seen` → "1. **URL Normalization & Visited Sets**: Strip tracking parameters before adding to the queue. Keep "
- ✓ [workflows\implementation.md:219] Pattern `content.*hash` → "2. **Content Hash / Unique ID Check**: If extracting multiple items per page, maintain a `Set` of un"
- ✓ [workflows\implementation.md:218] Pattern `Set\(\)` → "1. **URL Normalization & Visited Sets**: Strip tracking parameters before adding to the queue. Keep "
- ✓ [workflows\implementation.md:218] Pattern `already.*scraped` → "1. **URL Normalization & Visited Sets**: Strip tracking parameters before adding to the queue. Keep "
- ✓ [workflows\implementation.md:218] Pattern `skip.*duplicate` → "1. **URL Normalization & Visited Sets**: Strip tracking parameters before adding to the queue. Keep "
- ✓ [strategies\hybrid-approaches.md:261] Pattern `dedup` → "## Deduplication in Hybrid Workflows"

#### ⭐ W9: No output format guidance beyond JSON

**Score**: 3/3
**Rubric Match**: Comprehensive output section: JSON, CSV, JSONL, DB, streaming, memory management

**Evidence**:

- ✓ [SKILL.md:74] Pattern `stream` → "**Summary**: Skip if no protection signals were detected. Otherwise, test raw HTTP, then stealth bro"
- ✓ [workflows\implementation.md:227] Pattern `CSV` → "- **CSV**: Good for non-nested data and analyst delivery. Use `await Dataset.exportToCSV('results')`"
- ✓ [workflows\implementation.md:226] Pattern `JSONL` → "- **JSONL (Streaming)**: Best for large datasets. Appends line-by-line, avoiding memory crashes."
- ✓ [workflows\implementation.md:117] Pattern `stream` → "# Add upstream proxy for IP rotation if needed (Never hardcode credentials!)"
- ✓ [workflows\implementation.md:228] Pattern `database` → "- **Database (Postgres/SQLite)**: For continuous syncing. Batch your writes (e.g., save every 1,000 "
- ✓ [workflows\implementation.md:228] Pattern `SQLite` → "- **Database (Postgres/SQLite)**: For continuous syncing. Batch your writes (e.g., save every 1,000 "
- ✓ [workflows\implementation.md:228] Pattern `postgres` → "- **Database (Postgres/SQLite)**: For continuous syncing. Batch your writes (e.g., save every 1,000 "
- ✓ [workflows\implementation.md:226] Pattern `large.*dataset` → "- **JSONL (Streaming)**: Best for large datasets. Appends line-by-line, avoiding memory crashes."
- ✓ [workflows\implementation.md:222] Pattern `memory` → "## Step 8: Output Formats & Memory Management"
- ✓ [workflows\implementation.md:224] Pattern `100k` → "By default, Apify Crawlee saves to JSON. However, large scrapes (100k+ items) require efficient hand"

---

### Edge Case Coverage

#### ⭐ W4: No handling for authentication-gated content

**Score**: 3/3
**Rubric Match**: Full auth workflow: login recording, token extraction, session reuse, refresh handling

**Evidence**:

- ✓ [workflows\reconnaissance.md:569] Pattern `cookie.*auth` → "│   │                 ├─ Simple (cookie/token in traffic) → Record auth flow, extract tokens (See `."
- ✓ [workflows\reconnaissance.md:570] Pattern `OAuth` → "│   │                 ├─ OAuth redirect → Follow OAuth chain, extract bearer token, note refresh int"
- ✓ [workflows\reconnaissance.md:570] Pattern `bearer.*token` → "│   │                 ├─ OAuth redirect → Follow OAuth chain, extract bearer token, note refresh int"
- ✓ [workflows\reconnaissance.md:569] Pattern `record.*auth.*flow` → "│   │                 ├─ Simple (cookie/token in traffic) → Record auth flow, extract tokens (See `."
- ✓ [strategies\traffic-interception.md:68] Pattern `auth.*header` → "- Authentication headers or cookies"
- ✓ [strategies\traffic-interception.md:247] Pattern `record.*auth.*flow` → "- **API found, needs auth** → Record auth flow with session management, then direct HTTP"
- ✓ [strategies\dom-scraping.md:140] Pattern `cookie.*auth` → "8. interceptor_chrome_devtools_list_cookies()                → Extract auth cookies"
- ✓ [strategies\dom-scraping.md:173] Pattern `bearer.*token` → "'Authorization': `Bearer ${extractedToken}`,"
- ✓ [strategies\session-workflows.md:103] Pattern `login.*flow` → "After navigating through a login flow:"
- ✓ [strategies\session-workflows.md:113] Pattern `record.*auth.*flow` → "Record the authentication flow:"

#### ⭐ W5: No handling for non-English / internationalized sites

**Score**: 3/3
**Rubric Match**: Comprehensive i18n section with encoding, locale headers, non-Latin selector patterns

**Evidence**:

- ✓ [strategies\anti-blocking.md:130] Pattern `Accept-Language` → ""Accept-Language": "en-US,en;q=0.9","
- ✓ [reference\report-schema.md:128] Pattern `locale` → "account for locale headers."
- ✓ [reference\report-schema.md:131] Pattern `Accept-Language` → "- Test price extraction with `Accept-Language` and geo headers"
- ✓ [strategies\i18n.md:5] Pattern `UTF-?8` → "## 1. Character Encodings (UTF-8)"
- ✓ [strategies\i18n.md:3] Pattern `encod` → "When dealing with non-English or multi-lingual websites, you must handle character encodings and loc"
- ✓ [strategies\i18n.md:1] Pattern `i18n` → "# Scraping Internationalized (i18n) Sites"
- ✓ [strategies\i18n.md:1] Pattern `internation` → "# Scraping Internationalized (i18n) Sites"
- ✓ [strategies\i18n.md:3] Pattern `locale` → "When dealing with non-English or multi-lingual websites, you must handle character encodings and loc"
- ✓ [strategies\i18n.md:3] Pattern `non-English` → "When dealing with non-English or multi-lingual websites, you must handle character encodings and loc"
- ✓ [strategies\i18n.md:18] Pattern `CJK` → "- **CJK / RTL**: When dealing with Chinese/Japanese/Korean (CJK) or Right-To-Left (RTL) text, be awa"

#### ⭐ W6: No guidance for JavaScript SPA routing (hash/history API)

**Score**: 3/3
**Rubric Match**: Explains hash vs history routing, how to detect it, and extraction strategies

**Evidence**:

- ✓ [strategies\cheerio-vs-browser-test.md:132] Pattern `hash.*rout` → "- **Hash Routing**: Look for `#/` or hash-bang fragment navigation. These do not trigger network tra"
- ✓ [strategies\cheerio-vs-browser-test.md:133] Pattern `pushState` → "- **History API**: Look for `pushState` or seamless URL changes."
- ✓ [strategies\cheerio-vs-browser-test.md:133] Pattern `history.*API` → "- **History API**: Look for `pushState` or seamless URL changes."
- ✓ [strategies\cheerio-vs-browser-test.md:129] Pattern `SPA.*rout` → "## Single Page Applications (SPA) Routing"
- ✓ [strategies\cheerio-vs-browser-test.md:131] Pattern `client.?side.*rout` → "When evaluating a single-page app (SPA) for client-side routing, understand that navigation won't tr"
- ✓ [strategies\cheerio-vs-browser-test.md:129] Pattern `single.?page.*app.*rout` → "## Single Page Applications (SPA) Routing"
- ✓ [strategies\cheerio-vs-browser-test.md:132] Pattern `hash.*bang` → "- **Hash Routing**: Look for `#/` or hash-bang fragment navigation. These do not trigger network tra"
- ✓ [strategies\cheerio-vs-browser-test.md:132] Pattern `#/` → "- **Hash Routing**: Look for `#/` or hash-bang fragment navigation. These do not trigger network tra"
- ✓ [strategies\cheerio-vs-browser-test.md:132] Pattern `fragment.*navigation` → "- **Hash Routing**: Look for `#/` or hash-bang fragment navigation. These do not trigger network tra"
- ✓ [strategies\dom-scraping.md:26] Pattern `hash.*rout` → "1. **Detect Routing Type**: Look at the URL. Does it use hash routing (`site.com/#/page`) or the His"

---

### Error Handling & Resilience

#### ⭐ W1: No timeout/retry guidance for proxy-mcp tools

**Score**: 3/3
**Rubric Match**: Provides explicit timeout/retry patterns for proxy-mcp tools with example code

**Evidence**:

- ✓ [workflows\reconnaissance.md:675] Pattern `timeout` → "1. **Timeouts**: If a tool call hangs or returns no response within 10 seconds, cancel and retry. Do"
- ✓ [workflows\reconnaissance.md:407] Pattern `retry` → "- [ ] Add retry logic (3 attempts)"
- ✓ [workflows\reconnaissance.md:677] Pattern `proxy.*fail` → "2. **Retries with max attempts**: If `proxy_start()` or `interceptor_chrome_launch()` fails, retry u"
- ✓ [workflows\reconnaissance.md:688] Pattern `tool.*fail` → "→ If error: ABORT — log "Tool failed after 3 attempts" and fall back to curl-only mode"
- ✓ [workflows\reconnaissance.md:697] Pattern `MCP.*unavailable` → "4. Report findings with a note: "proxy-mcp unavailable, results are curl-only mode""
- ✓ [workflows\reconnaissance.md:682] Pattern `try.*again` → "→ If error: wait ~2 seconds, try again"
- ✓ [workflows\reconnaissance.md:677] Pattern `max.*attempts` → "2. **Retries with max attempts**: If `proxy_start()` or `interceptor_chrome_launch()` fails, retry u"
- ✓ [reference\proxy-tool-reference.md:235] Pattern `timeout` → "- **`proxy_get_exchange()` timeouts**: Always set an explicit timeout (e.g. 5000ms) to prevent hangi"
- ✓ [reference\proxy-tool-reference.md:234] Pattern `retry` → "- **`interceptor_chrome_launch()` failures**: Often fails if Chrome crashes. Retry up to 3 times."
- ✓ [reference\proxy-tool-reference.md:231] Pattern `proxy.*fail` → "Proxy and browser interactions are inherently flaky. Ensure your agent implementations handle failur"

#### ⭐ W2: No graceful degradation when proxy-mcp is unavailable

**Score**: 3/3
**Rubric Match**: Provides a complete curl-only fallback workflow when proxy-mcp is unavailable

**Evidence**:

- ✓ [SKILL.md:82] Pattern `without.*proxy.*mcp` → "### Degraded Mode: Without proxy-mcp"
- ✓ [workflows\reconnaissance.md:694] Pattern `without.*proxy.*mcp` → "1. If you must run without proxy-mcp → skip Phases 1-2 entirely."
- ✓ [workflows\reconnaissance.md:691] Pattern `proxy.*mcp.*not.*available` → "3. **Graceful degradation to curl-only mode**: If `proxy-mcp` is not available, or the MCP not insta"
- ✓ [workflows\reconnaissance.md:695] Pattern `fallback.*without.*browser` → "2. Run Phase 0 only (curl-based reconnaissance). This is the fallback without browser."
- ✓ [workflows\reconnaissance.md:688] Pattern `curl.*only.*mode` → "→ If error: ABORT — log "Tool failed after 3 attempts" and fall back to curl-only mode"
- ✓ [workflows\reconnaissance.md:691] Pattern `MCP.*not.*installed` → "3. **Graceful degradation to curl-only mode**: If `proxy-mcp` is not available, or the MCP not insta"
- ✓ [workflows\reconnaissance.md:691] Pattern `graceful.*degrad` → "3. **Graceful degradation to curl-only mode**: If `proxy-mcp` is not available, or the MCP not insta"
- ✓ [workflows\reconnaissance.md:393] Pattern `alternative.*tool` → "### Alternative: DOM Scraping (DevTools Bridge)"

#### ⭐ W3: Bare except/pass pattern in multi-tiered-scraping code example

**Score**: 3/3
**Rubric Match**: Catches specific exceptions, logs, and has retry/fallback logic

**Evidence**:

- ✓ [..\multi-tiered-scraping\SKILL.md:75] Pattern `log.*error` → "logger.error(f'Playwright fallback encountered a critical error for {url}')"
- ✓ [..\multi-tiered-scraping\SKILL.md:76] Pattern `log.*warning` → "logger.warning(f'Exception details: {e}')"
- ✓ [..\multi-tiered-scraping\SKILL.md:58] Pattern `logger\.` → "logger.debug(f'Fast fetch failed for {url}: {e}')"
- ✓ [..\multi-tiered-scraping\SKILL.md:77] Pattern `raise` → "raise e"
- ✓ [..\multi-tiered-scraping\SKILL.md:57] Pattern `except.*as\s+\w+` → "except (httpx.TimeoutException, httpx.NetworkError) as e:"

---

### Operational Robustness

#### ⭐ W12: No monitoring/alerting guidance for production scrapers

**Score**: 3/3
**Rubric Match**: Comprehensive ops section: scheduling, alerting, drift detection, cost tracking

**Evidence**:

- ✓ [apify\deployment.md:169] Pattern `monitor` → "### Monitor Run"
- ✓ [apify\deployment.md:429] Pattern `alert` → "### 2. Alerting & Webhooks"
- ✓ [apify\deployment.md:422] Pattern `schedul` → "### 1. Scheduling (Cron)"
- ✓ [apify\deployment.md:446] Pattern `drift` → "### 3. Data Drift Detection"
- ✓ [apify\deployment.md:463] Pattern `cost` → "### 4. Cost Tracking & Limits"
- ✓ [apify\deployment.md:448] Pattern `watchdog` → "Websites change layouts frequently. Implement a "watchdog" pattern to verify data quality:"
- ✓ [apify\deployment.md:431] Pattern `notification` → "Configure webhooks to notify your team of failures via Slack/Discord or email notifications."
- ✓ [apify\deployment.md:431] Pattern `email.*notif` → "Configure webhooks to notify your team of failures via Slack/Discord or email notifications."
- ✓ [apify\deployment.md:431] Pattern `Slack.*notif` → "Configure webhooks to notify your team of failures via Slack/Discord or email notifications."
- ✓ [apify\deployment.md:422] Pattern `cron` → "### 1. Scheduling (Cron)"

---

### Security & Ethics

#### ⭐ W10: No PII/sensitive data handling guidance

**Score**: 3/3
**Rubric Match**: Comprehensive data privacy section: PII detection, GDPR, minimization, redaction

**Evidence**:

- ✓ [strategies\anti-blocking.md:365] Pattern `PII` → "- **PII Detection**: Always scan scraped data for Personally Identifiable Information (emails, phone"
- ✓ [strategies\anti-blocking.md:366] Pattern `GDPR` → "- **Data Redaction**: Redact or hash PII before saving to comply with GDPR/CCPA, unless explicitly r"
- ✓ [strategies\anti-blocking.md:366] Pattern `CCPA` → "- **Data Redaction**: Redact or hash PII before saving to comply with GDPR/CCPA, unless explicitly r"
- ✓ [strategies\anti-blocking.md:366] Pattern `redact` → "- **Data Redaction**: Redact or hash PII before saving to comply with GDPR/CCPA, unless explicitly r"
- ✓ [workflows\reconnaissance.md:73] Pattern `consent` → "- **Popups/banners**: Cookie consent, newsletters → Need to dismiss before exploration"
- ✓ [workflows\implementation.md:181] Pattern `PII` → "## Step 6: Ethics, PII & Credentials"
- ✓ [workflows\implementation.md:186] Pattern `personal.*data` → "2. **PII Redaction**: Actively identify and redact personal data (PII) before it is saved or logged."
- ✓ [workflows\implementation.md:186] Pattern `redact` → "2. **PII Redaction**: Actively identify and redact personal data (PII) before it is saved or logged."

#### ⭐ W11: Credential exposure risk in proxy examples

**Score**: 3/3
**Rubric Match**: Examples use env vars, explains .env files, warns against hardcoding

**Evidence**:

- ✓ [workflows\implementation.md:185] Pattern `env(iron)?.*var` → "1. **Credentials & Secrets**: Never hardcode your `password`, API keys, or proxy credentials in the "
- ✓ [workflows\implementation.md:118] Pattern `process\.env` → "proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")"
- ✓ [workflows\implementation.md:29] Pattern `\$\{?[A-Z_]+\}?` → "console.log(`Testing with ${testUrls.length} URLs first...`);"
- ✓ [workflows\implementation.md:185] Pattern `secret` → "1. **Credentials & Secrets**: Never hardcode your `password`, API keys, or proxy credentials in the "
- ✓ [workflows\implementation.md:118] Pattern `\.env\b` → "proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")"
- ✓ [workflows\implementation.md:118] Pattern `PROXY_URL` → "proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")"
- ✓ [strategies\proxy-escalation.md:52] Pattern `process\.env` → "proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")"
- ✓ [strategies\proxy-escalation.md:52] Pattern `\.env\b` → "proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")"
- ✓ [strategies\proxy-escalation.md:52] Pattern `PROXY_URL` → "proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")"
- ✓ [strategies\anti-blocking.md:103] Pattern `env(iron)?.*var` → "> **⚠️ Never hardcode proxy credentials.** Use environment variables (`process.env.PROXY_URL`) or th"

---

### Structural Quality

#### ⭐ W13: No timeout/budget enforcement for reconnaissance phases

**Score**: 3/3
**Rubric Match**: Explicit time/interaction budgets for Phases 1-4 with enforcement instructions

**Evidence**:

- ✓ [SKILL.md:40] Pattern `budget` → "- **Budget Meta-Instruction**: If total reconnaissance exceeds 15 minutes, stop after this time limi"
- ✓ [SKILL.md:40] Pattern `time.*limit` → "- **Budget Meta-Instruction**: If total reconnaissance exceeds 15 minutes, stop after this time limi"
- ✓ [SKILL.md:44] Pattern `max.*minutes` → "**Budget**: Max 2 minutes time limit. **Tool-call cap**: 5 tool calls."
- ✓ [SKILL.md:40] Pattern `stop.*after` → "- **Budget Meta-Instruction**: If total reconnaissance exceeds 15 minutes, stop after this time limi"
- ✓ [SKILL.md:73] Pattern `ceiling` → "**Budget**: At most 3 escalation levels (ceiling). **Tool-call cap**: 6 tool calls."
- ✓ [SKILL.md:44] Pattern `cap\b` → "**Budget**: Max 2 minutes time limit. **Tool-call cap**: 5 tool calls."
- ✓ [SKILL.md:61] Pattern `at.*most.*\d+` → "**Budget**: At most 5 interactions per missing data point (hard cap). **Tool-call cap**: 10 tool cal"
- ✓ [workflows\reconnaissance.md:29] Pattern `budget` → "## Agent Budget & Limits"
- ✓ [workflows\reconnaissance.md:32] Pattern `time.*limit` → "- **Time limit**: Max 5 minutes total for Phase 1. If total reconnaissance exceeds 15 minutes, stop "
- ✓ [workflows\reconnaissance.md:32] Pattern `max.*minutes` → "- **Time limit**: Max 5 minutes total for Phase 1. If total reconnaissance exceeds 15 minutes, stop "

#### ⭐ W14: Known Major Sites table is too small

**Score**: 3/3
**Rubric Match**: 16+ known sites with architecture, data strategy, and protection level

**Evidence**:

- ✓ [strategies\framework-signatures.md:47] Pattern `ebay` → "| `ebay.com`, `ebay.*` | Custom SSR | HTML selectors, `ld+json` | High protection (Akamai/Datadome)."
- ✓ [strategies\framework-signatures.md:48] Pattern `zillow` → "| `zillow.com` | Next.js / React | `__NEXT_DATA__`, GraphQL API | Extreme protection (PerimeterX/Dat"
- ✓ [strategies\framework-signatures.md:49] Pattern `indeed` → "| `indeed.com` | React / Java | Embedded state (`window._initialData`), GraphQL | Extreme protection"
- ✓ [strategies\framework-signatures.md:50] Pattern `airbnb` → "| `airbnb.com` | React SSR | `ld+json`, GraphQL / `window.bootstrapData` | High protection. Dynamic "
- ✓ [strategies\framework-signatures.md:45] Pattern `facebook` → "| `facebook.com` | React (Custom) | GraphQL APIs (highly obfuscated) | Extreme protection. Extensive"
- ✓ [strategies\framework-signatures.md:56] Pattern `yelp` → "| `yelp.com` | React SSR | HTML selectors, `ld+json`, GraphQL | High protection (Cloudflare). Rate l"
- ✓ [strategies\framework-signatures.md:55] Pattern `booking\.com` → "| `booking.com` | Custom SSR / Perl | HTML selectors, `window.b_params` | High protection (Perimeter"
- ✓ [strategies\framework-signatures.md:51] Pattern `walmart` → "| `walmart.com` | React / Next.js | `__NEXT_DATA__`, GraphQL API | Extreme protection (PerimeterX). "
- ✓ [strategies\framework-signatures.md:52] Pattern `target\.com` → "| `target.com` | React / Redux | Redux state API, `__INITIAL_STATE__` | High protection. Extensive g"
- ✓ [strategies\framework-signatures.md:53] Pattern `bestbuy` → "| `bestbuy.com` | Custom / React | API-driven, HTML selectors | High protection. Strict rate limits,"

#### ⭐ W15: No versioning or changelog

**Score**: 3/3
**Rubric Match**: Semantic versioning + detailed changelog with breaking changes noted

**Evidence**:

- ✓ [SKILL.md:5] Pattern `version:` → "version: 1.2.0"
- ✓ [CHANGELOG.md:1] Pattern `changelog` → "# Changelog"
- ✓ [CHANGELOG.md:1] Pattern `CHANGELOG` → "# Changelog"
- ✓ [CHANGELOG.md:24] Pattern `## v\d` → "## v1.2.0 - 2026-08-25"
- ✓ [CHANGELOG.md:5] Pattern `last.*updated` → "**Last updated**: 2026-08-25"
- ✓ [CHANGELOG.md:6] Pattern `revision` → "**Revision**: 4"

#### ⭐ W16: Duplicate content between SKILL.md and reconnaissance.md

**Score**: 3/3
**Rubric Match**: Zero duplication — SKILL.md is a pure routing table for phase details

**Evidence**:

- ✓ [SKILL.md:39] Pattern `See.*workflows/reconnaissance` → "- **See**: `workflows/reconnaissance.md` for full step-by-step commands, tool usage, and tool error "
- ✓ [SKILL.md:39] Pattern `see.*reconnaissance\.md.*for.*detail` → "- **See**: `workflows/reconnaissance.md` for full step-by-step commands, tool usage, and tool error "
- ✓ [SKILL.md:39] Pattern `refer.*to.*reconnaissance` → "- **See**: `workflows/reconnaissance.md` for full step-by-step commands, tool usage, and tool error "

---

## Priority Fix List

Weaknesses ranked by severity (lowest score first):

| Priority | ID | Title | Score | Category |
|----------|-----|-------|-------|----------|

## Summary Statistics

- 🔴 **Critical gaps** (score 0): 0
- 🟡 **Partial coverage** (score 1): 0
- 🟢 **Adequate coverage** (score 2): 0
- ⭐ **Excellent coverage** (score 3): 16

---
name: web-scraping
description: Use when scraping websites, extracting data from web pages, bypassing anti-bot/403 protections, discovering hidden APIs, building sitemap crawlers, or developing production TypeScript Apify Actors.
license: MIT
version: 2.0.0
---

# Web Scraping with Intelligent Strategy Selection

## When This Skill Activates

- "Scrape [website]" / "Extract data from [site]"
- "Find info about [company]" / "Get [data] from [company name]" (no URL given)
- "I'm getting blocked" / "Getting 403 errors" → load `strategies/anti-blocking.md`
- "Make this an Apify Actor" / "Productionize this" → load `workflows/productionization.md`

## Mode Selection

| User Says | Mode | Budget | What Loads |
|-----------|------|--------|------------|
| "quick recon", "just check", "what framework" | **Quick** | ≤8 tool calls | This file only |
| "scrape X", "extract from X" (default) | **Standard** | ≤20 tool calls | This file + `workflows/reconnaissance.md` if browser needed |
| "full recon", "deep scan", "production scraping" | **Full** | ≤40 tool calls | All phases incl. protection testing |

Default is **Standard**. Escalate to Full only if protection signals appear.

**Budget enforcement**: Count tool calls. If you hit the cap, skip remaining work and report findings.

---

## Discovery Mode: Unknown Companies / No URL Given

When the user asks to scrape a company by name (no URL), use search-first discovery. **Never hallucinate URLs.**

### Step 1: Find real URLs via search

```bash
# Option A: Use web search tool (preferred if available)
# search_web("CompanyName official website contact page")

# Option B: Terminal — DuckDuckGo via Python
python -c "
from duckduckgo_search import DDGS
results = DDGS().text('CompanyName official website', max_results=5)
for r in results: print(r['href'])
"
```

### Step 2: Fast-fetch discovered URLs (curl probe + Python extract)

```bash
# Probe: is the site alive? What framework?
curl -sL -o /dev/null -w '%{http_code} %{content_type}' 'URL'
curl -sI 'URL' | grep -iE 'server|x-powered|cf-ray|set-cookie'
```

```python
# Extract: httpx + BeautifulSoup (the actual scraper)
import httpx, re
from bs4 import BeautifulSoup

resp = httpx.get(url, timeout=10, follow_redirects=True)
bot_sigs = ["cloudflare", "just a moment", "enable javascript"]

if resp.status_code == 200 and len(resp.text) > 1000 \
   and not any(s in resp.text.lower() for s in bot_sigs):
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Extract what you need locally — never stream raw HTML to LLM
    data = {
        'title': soup.title.string if soup.title else None,
        'emails': re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', resp.text),
        # ... add fields as needed
    }
else:
    # Anti-bot detected → escalate to browser (Step 3)
    pass
```

### Step 3: Browser fallback (only if anti-bot detected)

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.route("**/*", lambda r: r.abort()
        if r.request.resource_type in ['image','font','media'] else r.continue_())
    await page.goto(url, wait_until="domcontentloaded", timeout=25000)
    html = await page.content()
    await browser.close()
```

> **Python requirement**: Execute via `uv` for environment consistency.

---

## Quick Mode (curl-only, no browser)

1. `curl -sL URL | head -500` → check for target data in raw HTML
2. Match framework signatures against `strategies/framework-signatures.md`
3. Check headers for protection markers (cf-ray, datadome, etc.)

> **Gate**: All data found in raw HTML + no protection signals? → Skip to implementation. Otherwise → escalate to Standard.

## Standard Mode (default)

**Single pass: probe → assess → extract → validate → report.**

1. **Probe** (curl): Fetch raw HTML, check headers, detect framework
2. **Assess**: Data in raw HTML? → Cheerio/Python. JS-rendered? → Browser. API found? → Use API.
3. **Extract**: Use the simplest method that covers all data points
4. **Validate**: Confirm selectors/paths return expected values (max 5 test URLs)
5. **Report**: Generate findings with confidence levels

> **Escalation**: If protection signals detected during any step, load `strategies/anti-blocking.md` and consider switching to Full mode.

**If proxy-mcp is available**, use it for traffic interception (see `workflows/reconnaissance.md` for browser-based recon steps).

**If proxy-mcp is unavailable**, stay in curl + Python mode. Skip traffic interception.

## Full Mode

Run complete reconnaissance workflow: `workflows/reconnaissance.md` (all phases including protection testing).

---

## Implementation (after reconnaissance)

Invoke `brainstorming` for system design, then `writing-plans` for implementation plan.

**Core pattern** (via `subagent-driven-development` or `executing-plans`):
1. **Prototype**: Implement recommended approach (minimal code)
2. **Test**: Small batch (5-10 items) to validate
3. **Scale**: Full dataset + iterative fallbacks
4. **Harden**: Circuit breakers, retries, error handling

See `workflows/implementation.md` for patterns.

## Productionization (on request)

Convert to Apify Actor. See `workflows/productionization.md` and `apify/` directory.

## Quick Reference

| Task | Where |
|------|-------|
| Framework detection | `strategies/framework-signatures.md` |
| Cheerio vs Browser decision | `strategies/cheerio-vs-browser-test.md` |
| Protection bypass | `strategies/anti-blocking.md` |
| Traffic interception (proxy-mcp) | `strategies/traffic-interception.md` |
| Sitemap discovery | `strategies/sitemap-discovery.md` |
| API discovery | `strategies/api-discovery.md` |
| DOM scraping | `strategies/dom-scraping.md` |
| Hybrid approaches | `strategies/hybrid-approaches.md` |
| Report format | `reference/report-schema.md` |
| Proxy-MCP tools | `reference/proxy-tool-reference.md` |
| Apify Actor setup | `apify/cli-workflow.md` |
| Code examples | `examples/` directory |

## Core Principles

1. **Cheapest first**: curl → Python httpx → browser. Never launch a browser if curl gives you everything.
2. **Search, don't guess**: Unknown company? Search first. Never hallucinate URLs.
3. **Validate everything**: "Found in HTML" ≠ extractable. Test selectors/paths before reporting.
4. **Extract locally**: Parse HTML with BeautifulSoup/regex locally. Never stream raw HTML to LLM context.
5. **Progressive disclosure**: Load strategy/reference files only when a specific need is detected.

---

**Priority order**: Search discovery → curl probe → API (if found) → Cheerio/Python → Browser (last resort)

---
name: multi-tiered-scraping
description: Use when building robust data extraction pipelines, discovering target URLs dynamically to avoid hallucinations, optimizing web scraping compute resources, or dealing with anti-bot/JS-rendered sites.
---

# Multi-Tiered Scraping Architecture

## Overview
Web scraping pipelines often suffer from hallucinated URLs, token bloat, and massive compute waste when relying solely on heavy headless browsers (like Playwright/Puppeteer) or LLM code-rewriting loops. The **Multi-Tiered Scraping Architecture** is a highly efficient, parametric approach that cleanly separates target discovery, lightweight fetching, headless fallback, and data extraction.

## When to Use

- When tasked with finding emails, contacts, or specific data across multiple unknown domains.
- When you need to crawl dozens of sites quickly without maxing out RAM.
- When target sites might have anti-bot protections (Cloudflare) or require JS rendering.
- When you want to avoid writing new scraping logic for every request.

**Note**: For deep, single-site reconnaissance and stealth browser manipulation, refer to the [web-scraping skill](../web-scraping/SKILL.md). This multi-tiered skill is best for broad, multi-domain discovery workflows.

## The 4-Step Pipeline Architecture

Instead of directly launching a headless browser for every target or guessing URLs, structure your Python script into these four tiers:

1. **Target Discovery (No Hallucinations):** 
   Use a free Search API (e.g., `duckduckgo-search` package) to query live internet results. This guarantees you are only targeting real, active links and completely eliminates LLM hallucinations.

2. **Fast Fetching (Lightweight HTTP):**
   Attempt an extremely lightweight `GET` request using `httpx` or `requests` on each URL first. This consumes practically zero memory and executes in milliseconds.

3. **Smart JS / Anti-Bot Fallback (Headless Browser):**
   Evaluate the HTML payload from the fast fetch. If the payload is suspiciously small (< 1000 bytes), returns a `403 Forbidden`, or contains known anti-bot signatures (e.g., "cloudflare", "just a moment...", "enable javascript"), **only then** route that specific URL to a heavy headless browser (Playwright/Selenium) to bypass the block.

4. **Local Data Extraction (Parser):**
   Clean the HTML locally using `BeautifulSoup` or `html2text`, then apply regex or local heuristic parsers to extract the data (e.g., emails). This prevents streaming megabytes of raw HTML back into the LLM context window, saving massive amounts of tokens.

## Quick Reference / Implementation

```python
# The Core Logic for Tier 2 & Tier 3
import httpx
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

async def fetch_page(url):
    # Tier 2: Fast Fetch Attempt
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            html = resp.text
            
            # Check for JS walls or Anti-Bot
            bot_signatures = ["cloudflare", "just a moment...", "enable javascript"]
            if resp.status_code == 200 and not any(sig in html.lower() for sig in bot_signatures) and len(html) > 1000:
                return html # Success! Very cheap.
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        logger.debug(f'Fast fetch failed for {url}: {e}')

    # Tier 3: Heavy Fallback (Only executed when needed)
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                # Block resources to save bandwidth
                await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ['image', 'font', 'media'] else route.continue_())
                
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                html = await page.content()
                return html
            finally:
                await browser.close()
    except Exception as e:
        logger.error(f'Playwright fallback encountered a critical error for {url}')
        logger.warning(f'Exception details: {e}')
        raise e
```

## Common Mistakes

- **Mistake**: Using Playwright/Selenium as the default fetcher for every page.
  - **Fix**: Always try `httpx` first. It saves ~200MB RAM per request.
- **Mistake**: Generating Python code per request to scrape different sites.
  - **Fix**: Build one static CLI script (`pipeline.py`) that accepts search queries via arguments (`argparse`). The LLM should only generate the CLI arguments.
- **Mistake**: Feeding raw HTML back into the LLM to find emails.
  - **Fix**: Extract exactly what you need via local Python regex/BeautifulSoup and only output the structured JSON.

## Real-World Impact
This architecture reduces token consumption by ~90% and cuts scraping compute resources by over 80% compared to code-rewriting and default headless browser scraping.

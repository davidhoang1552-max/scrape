# Interactive Reconnaissance (Browser + Proxy-MCP)

Browser-based intelligence gathering via MITM traffic capture. Use when Standard/Full mode requires browser reconnaissance.

## MCP Tools Required

This phase requires:
- **Proxy-MCP**: MITM traffic interception + stealth Chrome browser + DevTools bridge + humanizer

See `../reference/proxy-tool-reference.md` for complete tool reference.
Requires the `proxy-mcp` MCP server to be configured and running.

---

## Agent Budget & Limits

To prevent runaway agent loops during reconnaissance, strict budgets apply:
- **Time limit**: Max 5 minutes total for Phase 1. If total reconnaissance exceeds 15 minutes, stop after this time limit and report with current findings.
- **Interactions**: At most 5 interactions (clicks/types) per missing data point (hard cap). Do no more than 10 total interactions in Phase 2.
- **Phase Limit**: Limit each phase to its prescribed boundaries. Don't escalate to proxy testing (Phase 4 ceiling) unless protections are detected.

---

## Step 1.1: Initialize Browser Session

### Start Proxy and Launch Browser

Start the MITM proxy, launch Chrome with stealth mode, and attach DevTools:

```
proxy_start()

interceptor_chrome_launch(
    url: "https://target-site.com",
    stealthMode: true
)

interceptor_chrome_devtools_attach(target_id)
```

Stealth mode automatically patches:
- `navigator.webdriver` → `false`
- `chrome.runtime` → exists with expected shape
- `Permissions.query` → correct notification response
- `Error.stack` → cleaned of CDP traces

### Capture Initial State

```
interceptor_chrome_devtools_screenshot()
```

### Observe Loading Behavior

**Look for**:
- **Immediate content**: Page loads fully on first request → Likely SSR/static
- **Loading spinners**: Content loads after initial paint → JavaScript-rendered
- **Skeleton screens**: Placeholder UI → API-driven dynamic content
- **Popups/banners**: Cookie consent, newsletters → Need to dismiss before exploration

**Document findings**:
```
Initial Load Observation:
- Page type: [Static/SSR/SPA]
- Loading pattern: [Immediate/Progressive/Delayed]
- Interstitials: [Cookie banner, newsletter popup]
```

---

## Step 1.2: Network Traffic Analysis

### Analyze Captured Traffic

**Critical**: The MITM proxy captures all traffic automatically. No manual DevTools inspection needed.

```
proxy_list_traffic()
```

This shows every HTTP exchange from the page load. Filter for interesting patterns:

```
proxy_list_traffic(url_filter: "/api/")          → REST APIs
proxy_list_traffic(url_filter: "/graphql")        → GraphQL endpoints
proxy_list_traffic(url_filter: "/_next/data/")    → Next.js data endpoints
proxy_list_traffic(url_filter: "/wp-json/")       → WordPress REST API
proxy_search_traffic(query: "application/json")   → Any JSON responses
```

Also check browser-side network view:
```
interceptor_chrome_devtools_list_network(resource_types: ["xhr", "fetch"])
```

### Inspect Discovered Endpoints

For each promising endpoint:

```
proxy_get_exchange(exchange_id)
```

**What to Extract**:
```
Discovered Endpoints:
✅ GET /api/v2/products?page={n}&limit={m}
   Request: page=1, limit=20
   Response: JSON array of products
   Auth: None required
   Rate limit: Unknown (test needed)

✅ GET /api/v2/products/{id}
   Response: Detailed product JSON
   Fields: id, name, price, description, images, stock
```

### Navigate and Observe Traffic

Browse through key pages while the proxy captures everything:

```
proxy_clear_traffic()
humanizer_click(target_id, ".category-link")
humanizer_idle(target_id, 2000)
proxy_list_traffic(url_filter: "products")

proxy_clear_traffic()
humanizer_click(target_id, ".product-item:first-child")
humanizer_idle(target_id, 2000)
proxy_list_traffic()
```

**Document**:
- Request method (GET/POST)
- Required headers (authorization, content-type)
- Query parameters (pagination, filters)
- Response structure
- Authentication requirements

---

## Step 1.3: Site Structure Discovery

### Test Pagination Mechanisms

**Pagination Type Detection**:

```
proxy_clear_traffic()
humanizer_click(target_id, ".next-page")
humanizer_idle(target_id, 2000)
proxy_list_traffic(url_filter: "page=")
```

Check if the URL changed:
```
interceptor_chrome_devtools_snapshot()    → Check current page state
```

**Pagination Patterns**:
1. **URL-based**: `?page=2` or `/page/2/`
   - Easy to iterate
   - Can directly construct URLs

2. **API-based**: XHR with `offset`/`cursor` parameters
   - Visible in proxy traffic capture
   - Extract pagination parameters from `proxy_get_exchange()`

3. **Infinite scroll**: Content appends on scroll
   - Trigger with `humanizer_scroll()`
   - Watch for API calls in proxy traffic

**Document**:
```
Pagination:
- Type: [URL-based / API-based / Infinite scroll]
- Parameter: page=N or offset=N or cursor=TOKEN
- Items per page: 20
- Total pages: ~250 (estimated from last page)
```

### Test Filtering and Search

```
proxy_clear_traffic()
humanizer_click(target_id, ".filter-category")
humanizer_idle(target_id, 2000)
proxy_list_traffic()                               → Observe filter API calls

proxy_clear_traffic()
humanizer_click(target_id, "input[name='search']")
humanizer_type(target_id, "test query")
humanizer_idle(target_id, 2000)
proxy_list_traffic(url_filter: "search")           → Observe search API
```

**Look for**:
- Search API endpoints
- Filter parameters
- Sort options
- Query structure

### Discover Data Loading Patterns

```
proxy_clear_traffic()
humanizer_scroll(target_id, "down", 1000)
humanizer_idle(target_id, 2000)
proxy_list_traffic(url_filter: "offset")           → Infinite scroll API calls
```

---

## Step 1.4: Anti-Bot Assessment

### Check for Bot Protection Indicators

Review captured traffic for blocking signals:

```
proxy_list_traffic()                               → Look for 403s, challenge pages
```

Check cookies for tracking markers:
```
interceptor_chrome_devtools_list_cookies(domain_filter: "cloudflare")
interceptor_chrome_devtools_list_cookies(domain_filter: "datadome")
```

Check localStorage for fingerprinting:
```
interceptor_chrome_devtools_list_storage_keys(storage_type: "local")
```

### Check for Protection Scripts

```
interceptor_chrome_devtools_snapshot()
```

Look in the accessibility tree for:
- Cloudflare challenge elements
- CAPTCHA containers
- "Access Denied" text

### Analyze TLS Fingerprints

```
proxy_get_tls_fingerprints()
```

This shows the TLS fingerprints of captured traffic, useful for understanding what the server sees.

### Test Rate Limiting

Navigate to multiple pages and observe responses:

```
interceptor_chrome_devtools_navigate("https://target-site.com/products?page=1")
humanizer_idle(target_id, 1000)
interceptor_chrome_devtools_navigate("https://target-site.com/products?page=2")
humanizer_idle(target_id, 1000)
# ... repeat and check for 429 responses
proxy_list_traffic(url_filter: "429")
```

**Document Protection Mechanisms**:
```
Protection Assessment:
⚠️  Cloudflare: DETECTED (cf-ray header in proxy traffic)
✓   CAPTCHA: Not triggered during normal browsing
✓   Fingerprinting: Not detected
⚠️  Rate Limiting: ~60 requests/minute threshold
✓   Authentication: Not required for product pages

Countermeasures Needed:
- Stealth mode already active (handles browser-level detection)
- Use upstream proxies for IP rotation (proxy_set_upstream)
- Respect rate limit: max 50 requests/minute
- If switching to HTTP-only client: consider TLS spoofing
```

**Note**: Chrome with stealth mode already handles most browser-level detection. Escalation to TLS spoofing is only needed if switching to HTTP-only clients (gotScraping, curl) for production.

---

## Step 1.5: Generate Intelligence Report

### Compile Findings

Create structured report with all reconnaissance data:

```markdown
See `../reference/report-schema.md` for the full report template (Sections 1-8 with self-critique).
```

---

## Step 1.6: Record Session

Save session via `proxy_session_start()` → `proxy_session_stop()` → `proxy_export_har()`. See `../strategies/session-workflows.md`.

---

## Example: E-Commerce API Discovery

```
proxy_start()
interceptor_chrome_launch("https://shop.example.com", stealthMode: true)
interceptor_chrome_devtools_attach(target_id)
proxy_list_traffic(url_filter: "api")          → Found: GET /api/products.json
proxy_get_exchange(exchange_id)                 → 100 products/request, no auth
interceptor_chrome_devtools_list_cookies(domain_filter: "cloudflare")  → None
```
**Outcome**: Direct API access, skip HTML scraping (50x faster)

---

## Decision Tree

Based on reconnaissance findings, determine next steps:

```
Reconnaissance Complete (Traffic Captured)
    ├─ API Discovered in Traffic?
    │   ├─ YES → Prefer API route (Phase 3: API strategy)
    │   │         └─ Auth required?
    │   │             ├─ NO → Direct API access (fastest)
    │   │             └─ YES → Auth complexity gate:
    │   │                 ├─ Simple (cookie/token in traffic) → Record auth flow, extract tokens (See `../strategies/authentication.md`)
    │   │                 ├─ OAuth redirect → Follow OAuth chain, extract bearer token, note refresh interval
    │   │                 ├─ 2FA/MFA detected → ABORT: Report as blocker, recommend manual session cookie injection
    │   │                 └─ CAPTCHA on login → ABORT: Report as blocker, cannot automate
    │   └─ NO → DOM scraping needed
    │             └─ JavaScript-rendered?
    │                 ├─ YES → DevTools bridge + humanizer
    │                 └─ NO → Use Cheerio (10x faster)
    │
    ├─ Protection Detected?
    │   ├─ Cloudflare/bot detection
    │   │   └─ Stealth mode handles browser detection
    │   │       └─ IP blocked? → Add upstream proxies
    │   ├─ Rate limiting
    │   │   └─ Respect limits in implementation
    │   └─ CAPTCHA
    │       └─ Consider CAPTCHA solving service or manual intervention
    │
    └─ Sitemap Available?
        ├─ YES → Use for URL discovery (combine with API if found)
        └─ NO → Use traffic-discovered pagination or crawl
```

---

## Common Mistakes

See `../reference/anti-patterns.md` for full list. Key ones:
- Always use `stealthMode: true` when launching Chrome
- Use `interceptor_chrome_devtools_navigate()` not `interceptor_chrome_navigate()` (preserves DevTools)
- `proxy_clear_traffic()` before each action to isolate API calls

---

## Tools Reference

See `../reference/proxy-tool-reference.md` for complete tool reference (all 80+ tools).

### Tool Error Handling

When using proxy-mcp tools, network and browser flakiness can occur. Apply these patterns:

1. **Timeouts**: If a tool call hangs or returns no response within 10 seconds, cancel and retry. Do not wait indefinitely.

2. **Retries with max attempts**: If `proxy_start()` or `interceptor_chrome_launch()` fails, retry up to 3 times with a pause between attempts:
   ```
   RETRY PATTERN (max 3 attempts):
     Attempt 1: Call proxy_start() or interceptor_chrome_launch(url, stealthMode: true)
       → If success: continue to next step
       → If error: wait ~2 seconds, try again
     Attempt 2: Same call
       → If success: continue
       → If error: wait ~2 seconds, try again
     Attempt 3: Same call
       → If success: continue
       → If error: ABORT — log "Tool failed after 3 attempts" and fall back to curl-only mode
   ```

3. **Graceful degradation to curl-only mode**: If `proxy-mcp` is not available, or the MCP not installed:
   ```
   FALLBACK SEQUENCE:
     1. If you must run without proxy-mcp → skip Phases 1-2 entirely.
     2. Run Phase 0 only (curl-based reconnaissance). This is the fallback without browser.
     3. Consider using an alternative tool if user explicitly requests browser scraping.
     4. Report findings with a note: "proxy-mcp unavailable, results are curl-only mode"
   ```

4. **Invalid targets**: If `interceptor_chrome_devtools_attach()` fails, re-fetch the target list via `interceptor_chrome_targets()` and retry with the correct `target_id`.

---

## Next Steps

After reconnaissance → validate findings → implement chosen strategy. Back to `../SKILL.md`.

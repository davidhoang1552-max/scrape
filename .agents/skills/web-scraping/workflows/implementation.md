# Phase 3: Iterative Implementation

Patterns for implementing scrapers incrementally, starting simple and adding complexity only as needed.

## Step 1: Implement Recommended Approach

### Progressive Enhancement Pattern

1. Start with minimal working code
2. Test with small sample (5-10 items)
3. Validate data quality
4. Scale to full dataset

### Reference Implementation Patterns

- **Traffic interception**: See `../strategies/traffic-interception.md`
- **Sitemap**: See `../strategies/sitemap-discovery.md`
- **API**: See `../strategies/api-discovery.md`
- **DOM scraping**: See `../strategies/dom-scraping.md`
- **Examples**: See `../examples/` directory

## Step 2: Test Small Batch First

```javascript
// Example: Test with first 10 URLs
const urls = await robots.parseUrlsFromSitemaps();
const testUrls = urls.slice(0, 10);

console.log(`Testing with ${testUrls.length} URLs first...`);
// Implement scraping logic
// Validate output quality
```

### Validation Checklist

- ✓ Data structure correct?
- ✓ All fields populated?
- ✓ Any errors or null values?
- ✓ Performance acceptable?

## Step 3: Scale or Fallback

### If Test Succeeds

```javascript
console.log('✓ Test successful, scaling to full dataset...');
await crawler.addRequests(urls); // All URLs
await crawler.run();
```

### Circuit Breaker (Required for Full-Scale Runs)

When scaling from test batch to full dataset, **always implement a circuit breaker** to prevent runaway failures. If the target starts returning errors at scale (rate limiting, IP bans, schema changes), the scraper must abort rather than burning through retries indefinitely.

```typescript
// Track consecutive failures — reset on success
let consecutiveFailures = 0;
const MAX_CONSECUTIVE_FAILURES = 10;

const crawler = new PlaywrightCrawler({
    maxRequestRetries: 3,

    async requestHandler({ page, request, log }) {
        // ... scraping logic ...

        // Reset on success
        consecutiveFailures = 0;
    },

    async failedRequestHandler({ request, error }, { log }) {
        consecutiveFailures++;
        log.error(`Failed: ${request.url} (${consecutiveFailures}/${MAX_CONSECUTIVE_FAILURES} consecutive)`);

        if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
            log.error('🛑 Circuit breaker tripped — aborting crawl.');
            // Save partial results before abort
            await crawler.autoscaledPool?.abort();
        }
    },
});
```

**Why this matters**:
- Prevents runaway compute costs (proxy fees, Apify CU)
- Stops IP reputation damage from hammering a blocking target
- Preserves partial results instead of losing everything to an infinite retry loop

### If Test Fails

```javascript
console.log('✗ Issues detected, falling back to alternative strategy...');
// Try next approach from recommendations
```

## Step 4: Handle Blocking (If Encountered)

### Identify Blocking Type

- **Rate limiting** → Slow down requests (`maxRequestsPerMinute`)
- **IP blocking** → Use proxies
- **Bot detection** → Use fingerprinting + proxies
- **Cloudflare/CAPTCHA** → Advanced techniques

### Apply Anti-Blocking

See `../strategies/anti-blocking.md` for complete guide.

**During development** (proxy-mcp):
```
# Stealth mode handles most browser-level detection
interceptor_chrome_launch(url, stealthMode: true)

# Add humanizer for behavioral anti-detection
humanizer_click(target_id, selector)
humanizer_idle(target_id, duration_ms)

# Add upstream proxy for IP rotation if needed (Never hardcode credentials!)
proxy_set_upstream(process.env.PROXY_URL || "http://127.0.0.1:8000")
```

**For production Actors** (Crawlee):
```typescript
const crawler = new PlaywrightCrawler({
    // Enable fingerprinting
    useSessionPool: true,
    fingerprintOptions: {
        devices: ['desktop'],
        operatingSystems: ['windows', 'macos'],
        browsers: ['chrome'],
    },

    // Add proxies
    proxyConfiguration: await Actor.createProxyConfiguration({
        groups: ['RESIDENTIAL'],
    }),

    // Slow down
    maxConcurrency: 3,
    maxRequestsPerMinute: 30,
});
```

### Test Incrementally

1. Start with stealth mode (proxy-mcp) or fingerprinting (Crawlee)
2. Add upstream proxies / datacenter proxies if still blocked
3. Upgrade to residential proxies if needed
4. Add session rotation

## Step 5: Add Robustness

### Error Handling Pattern

```javascript
const crawler = new PlaywrightCrawler({
    maxRequestRetries: 3,
    requestHandlerTimeoutSecs: 60,

    async requestHandler({ page, request, log }) {
        try {
            // Scraping logic
        } catch (error) {
            log.error(`Failed to scrape ${request.url}: ${error.message}`);
            throw error; // Retry
        }
    },

    failedRequestHandler({ request, error }, { log }) {
        log.error(`Request failed after retries: ${request.url}`);
    },
});
```

### Enhancements to Add

- Error handling (try/catch)
- Retries with exponential backoff
- Progress logging
- Rate limiting respect

## Step 6: Ethics, PII & Credentials

When scraping data, it is critical to handle sensitive information responsibly:

1. **Credentials & Secrets**: Never hardcode your `password`, API keys, or proxy credentials in the source code. Always use a `.env` file and load them via environment variables (e.g., `process.env.PROXY_URL`). Keep your secrets safe.
2. **PII Redaction**: Actively identify and redact personal data (PII) before it is saved or logged. Do not store sensitive information like phone numbers or emails unless explicitly required and legally permissible.
3. **Data Masking**: Mask or hash sensitive IDs, session tokens, or identifiable strings in your debug logs.

## Step 7: Data Validation & Quality

Schema validation (e.g., using JSON Schema, Ajv, or Zod) is critical to ensure data quality and perform type checking before saving scraped data. This prevents bad data from entering the dataset. Always assert types and validate schema!

```typescript
import { z } from 'zod';

const ProductSchema = z.object({
    id: z.string().min(1),
    title: z.string().min(3),
    price: z.number().positive(),
    inStock: z.boolean(),
});
type Product = z.infer<typeof ProductSchema>;

// Inside your requestHandler:
try {
    const data = ProductSchema.parse(scrapedData);
    await Dataset.pushData(data);
} catch (e) {
    log.warning(`Data validation failed for ${request.url}:`, e.errors);
    // Track failure rate: abort if >10% of records fail
}
```

## Step 7: Deduplication Strategy

Scraping via sitemaps and APIs can result in duplicate URLs/data. Ensure you have a deduplication strategy:

1. **URL Normalization & Visited Sets**: Strip tracking parameters before adding to the queue. Keep track of what you've seen using a `Set()` of visited URLs to skip duplicate requests for things already scraped.
2. **Content Hash / Unique ID Check**: If extracting multiple items per page, maintain a `Set` of unique IDs or a content hash of the item payload to prevent pushing duplicates.
3. **Post-Scrape Dedup**: Run a post-processing script to deduplicate by business key (e.g., SKU) before final delivery.

## Step 8: Output Formats & Memory Management

By default, Apify Crawlee saves to JSON. However, large scrapes (100k+ items) require efficient handling:

- **JSONL (Streaming)**: Best for large datasets. Appends line-by-line, avoiding memory crashes.
- **CSV**: Good for non-nested data and analyst delivery. Use `await Dataset.exportToCSV('results')`.
- **Database (Postgres/SQLite)**: For continuous syncing. Batch your writes (e.g., save every 1,000 items) rather than writing row-by-row or keeping everything in memory.
- **Memory Warning**: Never store the entire result set in an in-memory array (`const results = []`). Always push to a stream or external dataset immediately.

---

Back to main workflow: `../SKILL.md`

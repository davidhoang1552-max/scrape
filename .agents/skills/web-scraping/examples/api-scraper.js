/**
 * API-Based Scraper
 *
 * This example shows how to:
 * 1. Use APIs instead of scraping HTML
 * 2. Handle authentication (cookies, tokens)
 * 3. Process JSON responses
 * 4. Use bounded concurrency with backpressure (p-limit)
 * 5. Circuit breaker for failure resilience
 *
 * Use this pattern for: Any site with a discoverable API
 */

import { gotScraping } from 'got-scraping';
import { Dataset } from 'crawlee';
import { setTimeout } from 'timers/promises';
import pLimit from 'p-limit';

async function main() {
    // Example: Scrape products via API
    const baseApiUrl = 'https://api.example.com/v1';
    const productIds = [123, 456, 789]; // Get these from sitemap or exploration

    // Bounded concurrency: max 5 parallel requests (adjust based on rate limits)
    const limit = pLimit(5);

    // Circuit breaker state
    let consecutiveFailures = 0;
    const MAX_CONSECUTIVE_FAILURES = 10;
    let aborted = false;

    console.log(`🔍 Fetching ${productIds.length} products via API (concurrency: 5)...`);

    const tasks = productIds.map((id) =>
        limit(async () => {
            if (aborted) return; // Skip remaining after circuit breaker trips

            try {
                console.log(`Fetching product ${id}...`);

                const response = await gotScraping({
                    url: `${baseApiUrl}/products/${id}`,
                    responseType: 'json',
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (compatible; Scraper/1.0)',
                        // Add authentication if needed:
                        // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
                        // 'X-API-Key': process.env.API_KEY,
                    },
                    timeout: {
                        request: 10000, // 10 second timeout
                    },
                    retry: {
                        limit: 3,
                        methods: ['GET'],
                    },
                });

                // Stream to Dataset — never accumulate in memory
                const product = response.body;
                await Dataset.pushData({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    inStock: product.in_stock,
                    scrapedAt: new Date().toISOString(),
                });

                console.log(`✓ Fetched: ${product.name}`);
                consecutiveFailures = 0; // Reset on success

                // Rate limiting (respect API limits)
                await setTimeout(100); // 100ms delay = 10 requests/second per worker

            } catch (error) {
                consecutiveFailures++;

                if (error.response?.statusCode === 404) {
                    console.log(`✗ Product ${id} not found`);
                } else if (error.response?.statusCode === 429) {
                    console.log(`⚠ Rate limited, waiting 5 seconds...`);
                    await setTimeout(5000);
                } else {
                    console.error(`✗ Error fetching product ${id}:`, error.message);
                }

                // Circuit breaker: abort if too many consecutive failures
                if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
                    console.error(`🛑 Circuit breaker tripped: ${consecutiveFailures} consecutive failures. Aborting.`);
                    aborted = true;
                }
            }
        })
    );

    await Promise.allSettled(tasks);

    const dataset = await Dataset.getData();
    console.log(`✓ Fetched ${dataset.items.length}/${productIds.length} products`);
}

main();


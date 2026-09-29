# Authentication Strategy

Guidance for handling authentication-gated content during scraping. 

## Overview

Many sites require authentication to access data (e.g., LinkedIn, B2B portals, user dashboards). 
Scraping behind login walls requires distinct workflows from public scraping:

1. **Authentication Reconnaissance**: Understanding the login flow.
2. **Session Acquisition**: Automating the login or manually extracting cookies.
3. **Session Replay**: Attaching tokens/cookies to scraper requests.
4. **Session Maintenance**: Handling expiration and token refresh.

## 1. Authentication Reconnaissance

Use the MITM proxy to record the login flow:

```bash
proxy_start()
interceptor_chrome_launch("https://target.com/login", stealthMode: true)
interceptor_chrome_devtools_attach(target_id)
proxy_clear_traffic()

# Perform login via humanizer or manually
humanizer_type(target_id, "username_field", "user@example.com")
humanizer_type(target_id, "password_field", "securepassword")
humanizer_click(target_id, "submit_button")
humanizer_idle(target_id, 3000)
```

**What to look for in traffic (`proxy_list_traffic()`)**:
- Does it use a simple `POST /login` form?
- Are there CSRF tokens required in the payload?
- Is it an OAuth flow (redirects to Google/Microsoft)?
- Does it return a Bearer token or set `HttpOnly` cookies?
- Are there CAPTCHAs during login?

## 2. Session Acquisition

### Approach A: Manual Cookie Extraction (Best for High Security)

If the login is heavily protected by CAPTCHAs or 2FA, do not automate it. Log in manually in a normal browser, extract the session cookies, and provide them as input to your scraper.

1. Log in manually.
2. Export cookies (e.g., using EditThisCookie extension or DevTools).
3. Pass cookies to the scraper via `actor.json` input or environment variables.

### Approach B: Automated Login (Best for Low Security)

If the login is a simple form, automate it within your crawler:

```typescript
// Playwright Crawler Example
const crawler = new PlaywrightCrawler({
    async requestHandler({ page, request }) {
        if (request.userData.isLogin) {
            await page.goto('https://target.com/login');
            await page.fill('#username', process.env.SCRAPER_USER);
            await page.fill('#password', process.env.SCRAPER_PASS);
            await page.click('button[type="submit"]');
            await page.waitForNavigation();
            
            // Save cookies to session state
            const cookies = await page.context().cookies();
            // ... store cookies ...
            return;
        }
        // ... proceed with normal scraping ...
    }
});
```

## 3. Session Replay

Once you have the authentication tokens or cookies, inject them into your scraping requests:

### With CheerioCrawler / HTTP Clients

If the site uses Bearer tokens:

```typescript
const response = await gotScraping({
    url: 'https://api.target.com/data',
    headers: {
        'Authorization': `Bearer ${sessionToken}`,
    },
});
```

If the site uses Cookies:

```typescript
const response = await gotScraping({
    url: 'https://target.com/data',
    headers: {
        'Cookie': `session_id=${sessionId}; user_token=${userToken}`,
    },
});
```

## 4. Session Maintenance & Token Refresh

Sessions expire. Your scraper must detect expiration and handle it gracefully.

1. **Detect Expiration**: Check for HTTP 401 Unauthorized or redirects to `/login`.
2. **Refresh Logic**: If using OAuth or JWT, implement the refresh token endpoint. If using cookies, trigger the automated login flow again or pause the scraper and alert the operator if manual login is required.

```typescript
if (response.statusCode === 401) {
    log.warning('Session expired. Attempting refresh...');
    await refreshSession();
    // Retry request
}
```

## When to Give Up

Do not attempt to bypass or automate login flows that strictly require:
- Hardware keys (YubiKey)
- SMS / Email 2FA (unless you have API access to a dedicated phone/email inbox)
- Complex behavioral CAPTCHAs on every login attempt

In these scenarios, **Manual Cookie Extraction** (Approach A) is the only viable path.

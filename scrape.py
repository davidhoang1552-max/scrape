"""
Unified Web Scraper
Reads target companies from a CSV and outputs results with timestamps.
Usage: python scrape.py [--input companies.csv]
"""
import asyncio, csv, json, re, urllib.parse
import httpx
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

# ── Email Extraction & Validation ─────────────────────────────────────────────

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

JUNK_DOMAINS = {
    'example.com', 'domain.com', 'email.com', 'gmail.com', 'yahoo.com', 'hotmail.com',
    'outlook.com', 'test.com', 'sentry.io', 'wixpress.com', 'schema.org', 'w3.org',
    'fontawesome.com', 'bootstrap.com', 'jquery.com', 'google.com', 'state.gov',
    'lg.edu', 'lgpartner.com', 'github.com', 'sentry-cdn.com', 'gravatar.com',
    'googleapis.com', 'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
    'youtube.com', 'tiktok.com', 'apple.com', 'microsoft.com', 'cloudflare.com',
    'png', 'jpg', 'jpeg', 'svg'
}

JUNK_LOCALS = {
    'user', 'name', 'email', 'yourname', 'username', 'info_example',
    'test', 'admin_test', 'sample', 'abc', 'xyz', 'foo', 'bar', 'privacy',
    'info', 'your', 'someone'
}

JUNK_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js')

def valid_email(e):
    local, _, domain = e.partition('@')
    if not domain: return False
    if domain.lower() in JUNK_DOMAINS: return False
    if local.lower() in JUNK_LOCALS: return False
    if any(domain.lower().endswith(ext) for ext in JUNK_EXTENSIONS): return False
    if len(e) > 80 or len(local) < 2: return False
    return True

def extract(text):
    if not text: return set()
    return {e for e in EMAIL_RE.findall(text) if valid_email(e)}

# ── Async Scraper ─────────────────────────────────────────────────────────────

CONTACT_KEYWORDS = ('contact', 'lien-he', 'about', 'imprint', 'support', 'reach-us')

async def fetch(client, url):
    if not url: return ""
    try:
        r = await client.get(url, timeout=8.0, follow_redirects=True)
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""

async def scrape_one(client, sem, name, url, region):
    async with sem:
        emails = set()
        html = await fetch(client, url)
        emails.update(extract(html))

        # Check contact/about pages if homepage had no emails
        if not emails and html:
            base = urllib.parse.urlparse(url).netloc
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                href_l = a['href'].lower()
                if any(k in href_l for k in CONTACT_KEYWORDS):
                    full = urllib.parse.urljoin(url, a['href'])
                    if urllib.parse.urlparse(full).netloc == base:
                        emails.update(extract(await fetch(client, full)))
                        if emails: break

        result = {"name": name, "region": region, "url": url, "emails": sorted(emails)}
        tag = "VN" if region == "Vietnam" else "INTL"
        count = len(emails)
        print(f"[{tag}] {name} -> {count} email(s)" + (f": {result['emails'][:3]}" if count else ""))
        return result

async def main():
    parser = argparse.ArgumentParser(description="Scrape company emails")
    parser.add_argument("--input", default="companies.csv", help="Input CSV file")
    args = parser.parse_args()

    companies = []
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append(row)
    except FileNotFoundError:
        print(f"Error: {args.input} not found.")
        return

    sem = asyncio.Semaphore(25)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    async with httpx.AsyncClient(headers=headers, verify=True) as client:
        tasks = [scrape_one(client, sem, c["name"], c["url"], c["region"]) for c in companies]
        results = await asyncio.gather(*tasks)

    # Output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_out = f"results_{timestamp}.json"
    csv_out = f"results_{timestamp}.csv"

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(csv_out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Company", "Region", "Website", "Emails"])
        for r in results:
            w.writerow([r["name"], r["region"], r["url"], "; ".join(r["emails"])])

    vn_r = [r for r in results if r["region"] == "Vietnam"]
    intl_r = [r for r in results if r["region"] == "International"]
    vn_hit = len([r for r in vn_r if r["emails"]])
    intl_hit = len([r for r in intl_r if r["emails"]])
    total_emails = sum(len(r["emails"]) for r in results)

    print(f"\n{'='*50}")
    print(f"DONE: {len(results)} companies (VN:{len(vn_r)} INTL:{len(intl_r)})")
    print(f"Emails found: VN {vn_hit}/{len(vn_r)} | INTL {intl_hit}/{len(intl_r)} | Total unique emails: {total_emails}")
    print(f"Saved: {json_out} + {csv_out}")

if __name__ == "__main__":
    asyncio.run(main())

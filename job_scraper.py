# ─────────────────────────────────────────────
#  job_scraper.py
#  Uses Playwright to search Naukri.com and Indeed
#  for jobs based on keywords from the resume
# ─────────────────────────────────────────────
import asyncio
import sys
from playwright.async_api import async_playwright

# Fix for Playwright + Streamlit on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ── Config ──────────────────────────────────────────────────────────────────
MAX_JOBS_PER_KEYWORD = 5   # How many jobs to grab per keyword per site
PAGE_TIMEOUT_MS      = 15000  # 15 seconds timeout for page loads


# ── Naukri Scraper ───────────────────────────────────────────────────────────

async def scrape_naukri(page, keyword: str) -> list[dict]:
    """
    Searches Naukri.com for a given keyword and returns a list of job dicts.
    Each dict has: title, company, url, source
    """
    jobs = []
    search_url = f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs"

    try:
        await page.goto(search_url, timeout=PAGE_TIMEOUT_MS)
        await page.wait_for_timeout(2000)  # let the JS render

        # Each job card on Naukri has this structure
        job_cards = await page.query_selector_all("article.jobTuple")

        for card in job_cards[:MAX_JOBS_PER_KEYWORD]:
            try:
                title_el   = await card.query_selector("a.title")
                company_el = await card.query_selector("a.subTitle")

                title   = await title_el.inner_text()   if title_el   else "N/A"
                company = await company_el.inner_text() if company_el else "N/A"
                url     = await title_el.get_attribute("href") if title_el else ""

                if url:
                    jobs.append({
                        "title"  : title.strip(),
                        "company": company.strip(),
                        "url"    : url.strip(),
                        "source" : "Naukri",
                    })
            except Exception:
                continue  # skip broken cards silently

    except Exception as e:
        print(f"[Naukri] Failed for keyword '{keyword}': {e}")

    return jobs


# ── Indeed Scraper ───────────────────────────────────────────────────────────

async def scrape_indeed(page, keyword: str) -> list[dict]:
    """
    Searches Indeed.co.in for a given keyword and returns a list of job dicts.
    Each dict has: title, company, url, source
    """
    jobs = []
    query      = keyword.replace(" ", "+")
    search_url = f"https://in.indeed.com/jobs?q={query}&sort=date"

    try:
        await page.goto(search_url, timeout=PAGE_TIMEOUT_MS)
        await page.wait_for_timeout(2000)

        job_cards = await page.query_selector_all("div.job_seen_beacon")

        for card in job_cards[:MAX_JOBS_PER_KEYWORD]:
            try:
                title_el   = await card.query_selector("h2.jobTitle span")
                company_el = await card.query_selector("span.companyName")
                link_el    = await card.query_selector("h2.jobTitle a")

                title   = await title_el.inner_text()   if title_el   else "N/A"
                company = await company_el.inner_text() if company_el else "N/A"
                href    = await link_el.get_attribute("href") if link_el else ""

                if href:
                    full_url = f"https://in.indeed.com{href}" if href.startswith("/") else href
                    jobs.append({
                        "title"  : title.strip(),
                        "company": company.strip(),
                        "url"    : full_url.strip(),
                        "source" : "Indeed",
                    })
            except Exception:
                continue

    except Exception as e:
        print(f"[Indeed] Failed for keyword '{keyword}': {e}")

    return jobs


# ── Main Scrape Function ─────────────────────────────────────────────────────

async def scrape_jobs_for_keywords(keywords: list[str]) -> list[dict]:
    """
    Loops through all keywords, searches both sites,
    and returns one combined flat list of all jobs found.
    """
    all_jobs = []

    # Only use top 5 keywords to avoid being too slow
    top_keywords = keywords[:5]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for keyword in top_keywords:
            print(f"[Scraper] Searching for: {keyword}")

            naukri_jobs = await scrape_naukri(page, keyword)
            indeed_jobs = await scrape_indeed(page, keyword)

            all_jobs.extend(naukri_jobs)
            all_jobs.extend(indeed_jobs)

            await asyncio.sleep(1)  # polite delay between searches

        await browser.close()

    # Remove duplicate URLs across keywords
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)

    print(f"[Scraper] Total unique jobs found: {len(unique_jobs)}")
    return unique_jobs


def run_scraper(keywords: list[str]) -> list[dict]:
    """
    Sync wrapper so Streamlit (which is not async) can call this easily.
    """
    return asyncio.run(scrape_jobs_for_keywords(keywords))

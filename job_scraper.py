import asyncio
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

MAX_JOBS_PER_KEYWORD = 5
PAGE_TIMEOUT_MS      = 15000


async def scrape_naukri(page, keyword):
    jobs = []
    search_url = f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs"
    try:
        await page.goto(search_url, timeout=PAGE_TIMEOUT_MS)
        await page.wait_for_timeout(2000)
        job_cards = await page.query_selector_all("article.jobTuple")
        for card in job_cards[:MAX_JOBS_PER_KEYWORD]:
            try:
                title_el   = await card.query_selector("a.title")
                company_el = await card.query_selector("a.subTitle")
                title   = await title_el.inner_text()   if title_el   else "N/A"
                company = await company_el.inner_text() if company_el else "N/A"
                url     = await title_el.get_attribute("href") if title_el else ""
                if url:
                    jobs.append({"title": title.strip(), "company": company.strip(), "url": url.strip(), "source": "Naukri"})
            except Exception:
                continue
    except Exception as e:
        print(f"[Naukri] Failed for keyword '{keyword}': {e}")
    return jobs


async def scrape_indeed(page, keyword):
    jobs = []
    query      = keyword.replace(" ", "+")
    search_url = f"https://in.indeed.com/jobs?q={query}&sort=date"
    try:
        await page.goto(search_url, timeout=PAGE_TIMEOUT_MS)
        await page.wait_for_timeout(2000)
        job_cards = await page.query_selector_all("div.job_seen_beacon")
        for card in job_cards[:MAX_JOBS_PER_KEYWORD]:
            try:

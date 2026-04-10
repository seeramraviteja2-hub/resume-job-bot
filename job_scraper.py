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
                title_el   = await card.query_selector("h2.jobTitle span")
                company_el = await card.query_selector("span.companyName")
                link_el    = await card.query_selector("h2.jobTitle a")
                title   = await title_el.inner_text()   if title_el   else "N/A"
                company = await company_el.inner_text() if company_el else "N/A"
                href    = await link_el.get_attribute("href") if link_el else ""
                if href:
                    full_url = f"https://in.indeed.com{href}" if href.startswith("/") else href
                    jobs.append({"title": title.strip(), "company": company.strip(), "url": full_url.strip(), "source": "Indeed"})
            except Exception:
                continue
    except Exception as e:
        print(f"[Indeed] Failed for keyword '{keyword}': {e}")
    return jobs


async def scrape_jobs_for_keywords(keywords):
    all_jobs = []
    top_keywords = keywords[:5]

    async with async_playwright() as pw:
        # ── These args make Playwright work on Streamlit Cloud ──
       browser = await pw.chromium.launch(
    headless=True,
    executable_path="/usr/bin/chromium",
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--single-process",
        "--disable-gpu",
    ]
)
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
            await asyncio.sleep(1)

        await browser.close()

    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)

    print(f"[Scraper] Total unique jobs found: {len(unique_jobs)}")
    return unique_jobs


def run_scraper(keywords):
    return asyncio.run(scrape_jobs_for_keywords(keywords))

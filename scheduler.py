
import os
import json
from job_scraper import run_scraper
from database    import create_tables, filter_new_jobs, get_all_users
from mailer      import send_jobs_email


def run_daily_scan():
    """
    Main function — called by GitHub Actions every morning.
    Loops through all registered users and sends new job alerts.
    """
    print("=" * 50)
    print("🤖 Daily Job Scan Started")
    print("=" * 50)

    # Make sure tables exist (important for first run)
    create_tables()

    # Load all users who registered via the Streamlit app
    users = get_all_users()

    if not users:
        print("⚠️  No users registered yet. Someone needs to sign up via the app first.")
        return

    print(f"👥 Found {len(users)} registered user(s)\n")

    for user in users:
        email    = user["email"]
        keywords = user["keywords"]

        print(f"🔍 Scanning jobs for: {email}")
        print(f"   Keywords: {', '.join(keywords[:5])}")

        # Scrape jobs from Naukri and Indeed
        all_jobs = run_scraper(keywords)
        print(f"   Total jobs found: {len(all_jobs)}")

        # Filter out jobs this user has already seen
        new_jobs = filter_new_jobs(email, all_jobs)
        print(f"   New jobs (not seen before): {len(new_jobs)}")

        if not new_jobs:
            print(f"   ✅ No new jobs for {email} today. Skipping email.\n")
            continue

        # Get sender credentials from GitHub Secrets (set as env variables)
        sender_email    = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            print("   ❌ SENDER_EMAIL or SENDER_PASSWORD not set in GitHub Secrets!")
            continue

        # Send the email
        sent = send_jobs_email(
            to_email        = email,
            jobs            = new_jobs,
            keywords        = keywords,
            sender_email    = sender_email,
            sender_password = sender_password,
        )

        if sent:
            print(f"   📧 Email sent to {email} with {len(new_jobs)} new jobs!\n")
        else:
            print(f"   ❌ Failed to send email to {email}\n")

    print("=" * 50)
    print("✅ Daily scan complete!")
    print("=" * 50)


if __name__ == "__main__":
    run_daily_scan()

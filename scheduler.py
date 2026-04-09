import os
from job_scraper import run_scraper
from database import filter_new_jobs, get_all_users
from mailer import send_email


def main():
    print("🚀 Scheduler started...")

    # Get sender credentials from environment (GitHub Secrets)
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("❌ Missing email credentials in environment variables")
        return

    # Get all registered users
    users = get_all_users()

    if not users:
        print("⚠️ No users found in users.json")
        return

    # Loop through each user
    for user in users:
        try:
            email = user["email"]
            keywords = user["keywords"]

            print(f"\n🔍 Processing user: {email}")
            print(f"📌 Keywords: {keywords}")

            # Step 1: Scrape jobs
            jobs = run_scraper(keywords)

            if not jobs:
                print("⚠️ No jobs scraped")
                continue

            # Step 2: Filter new jobs (this ALSO saves to DB)
            new_jobs = filter_new_jobs(email, jobs)

            if not new_jobs:
                print("✅ No new jobs found")
                continue

            print(f"📨 Found {len(new_jobs)} new jobs")

            # Step 3: Send email
            send_email(
                sender_email=sender_email,
                sender_password=sender_password,
                receiver_email=email,
                jobs=new_jobs
            )

            print("✅ Email sent successfully")

        except Exception as e:
            print(f"❌ Error processing user {user.get('email', 'unknown')}: {e}")


if __name__ == "__main__":
    main() seen_jobs]
        
        if new_jobs:
            print(f"Found {len(new_jobs)} new jobs")
            
            # Send email with results
            send_jobs_email(
                to_email=os.getenv("RECIPIENT_EMAIL"),
                jobs=new_jobs,
                keywords=resume_skills,
                sender_email=os.getenv("SENDER_EMAIL"),
                sender_password=os.getenv("SENDER_PASSWORD")
            )
            
            # Save jobs to database
            save_jobs(new_jobs)
            print("Job scan completed successfully")
        else:
            print("No new jobs found")
            
    except Exception as e:
        print(f"Error during job scan: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

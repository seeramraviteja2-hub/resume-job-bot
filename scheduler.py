#!/usr/bin/env python3
"""
Daily job scan scheduler that scrapes jobs and emails results.
"""

import os
import sys
from job_scraper import scrape_jobs
from resume_parser import parse_resume
from mailer import send_email
from database import save_jobs, get_seen_jobs

def main():
    """Main scheduler function."""
    try:
        # Scrape jobs
        print("Starting job scrape...")
        jobs = scrape_jobs()
        
        # Get previously seen jobs to avoid duplicates
        seen_jobs = get_seen_jobs()
        
        # Filter for new jobs only
        new_jobs = [job for job in jobs if job['id'] not in seen_jobs]
        
        if new_jobs:
            print(f"Found {len(new_jobs)} new jobs")
            
            # Parse resume and match jobs
            resume_skills = parse_resume()
            
            # Send email with results
            send_email(new_jobs, resume_skills)
            
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
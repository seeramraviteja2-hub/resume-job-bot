#!/usr/bin/env python3
"""
Daily job scan scheduler that scrapes jobs and emails results.
"""

import os
import sys
from job_scraper import run_scraper
from resume_parser import parse_resume
from mailer import send_email
from database import save_jobs, get_seen_jobs

def main():
    """Main scheduler function."""
    try:
        # Parse resume and extract keywords
        print("Parsing resume...")
        resume_skills = parse_resume()
        
        # Scrape jobs using resume keywords
        print("Starting job scrape...")
        jobs = run_scraper(resume_skills)
        
        # Get previously seen jobs to avoid duplicates
        seen_jobs = get_seen_jobs()
        
        # Filter for new jobs only
        new_jobs = [job for job in jobs if job['id'] not in seen_jobs]
        
        if new_jobs:
            print(f"Found {len(new_jobs)} new jobs")
            
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
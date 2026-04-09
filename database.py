# ─────────────────────────────────────────────
#  database.py
#  Tracks which jobs have already been sent to each user
#  so we never send the same job twice
# ─────────────────────────────────────────────

import sqlite3
import os


# The database file will be created in the project folder
DB_PATH = "seen_jobs.db"


def get_connection():
    """Opens and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def create_tables():
    """
    Creates the 'seen_jobs' table if it doesn't already exist.
    Call this once at app startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email  TEXT    NOT NULL,
            job_url     TEXT    NOT NULL,
            job_title   TEXT,
            company     TEXT,
            seen_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Make sure the same URL is never stored twice for the same user
            UNIQUE(user_email, job_url)
        )
    """)

    conn.commit()
    conn.close()


def is_job_already_seen(user_email: str, job_url: str) -> bool:
    """
    Returns True if this job URL was already sent to this user before.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM seen_jobs
        WHERE user_email = ? AND job_url = ?
    """, (user_email, job_url))

    result = cursor.fetchone()
    conn.close()

    return result is not None


def mark_job_as_seen(user_email: str, job_url: str, job_title: str, company: str):
    """
    Saves a job to the database so it won't be sent again.
    Silently ignores if it already exists (IGNORE conflict strategy).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO seen_jobs (user_email, job_url, job_title, company)
        VALUES (?, ?, ?, ?)
    """, (user_email, job_url, job_title, company))

    conn.commit()
    conn.close()


def filter_new_jobs(user_email: str, jobs: list[dict]) -> list[dict]:
    """
    Takes a list of scraped jobs and returns ONLY the ones
    the user has never seen before. Also marks them as seen.

    Each job dict must have: url, title, company
    """
    new_jobs = []

    for job in jobs:
        if not is_job_already_seen(user_email, job["url"]):
            new_jobs.append(job)
            mark_job_as_seen(user_email, job["url"], job["title"], job["company"])

    return new_jobs


def get_user_job_count(user_email: str) -> int:
    """Returns how many jobs have been sent to this user in total."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM seen_jobs WHERE user_email = ?
    """, (user_email,))

    count = cursor.fetchone()[0]
    conn.close()

    return count

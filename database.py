import sqlite3
import json
import os

DB_PATH    = "seen_jobs.db"
USERS_PATH = "users.json"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
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
            UNIQUE(user_email, job_url)
        )
    """)
    conn.commit()
    conn.close()

def register_user(email, keywords, sender_email, sender_password):
    users = _load_users()
    users[email] = {
        "email": email,
        "keywords": keywords,
        "sender_email": sender_email,
        "sender_password": sender_password,
    }
    _save_users(users)

def get_all_users():
    users = _load_users()
    return list(users.values())

def _load_users():
    if not os.path.exists(USERS_PATH):
        return {}
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def _save_users(users):
    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)

def is_job_already_seen(user_email, job_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM seen_jobs WHERE user_email = ? AND job_url = ?",
        (user_email, job_url)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_job_as_seen(user_email, job_url, job_title, company):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO seen_jobs (user_email, job_url, job_title, company) VALUES (?, ?, ?, ?)",
        (user_email, job_url, job_title, company)
    )
    conn.commit()
    conn.close()

def filter_new_jobs(user_email, jobs):
    new_jobs = []
    for job in jobs:
        if not is_job_already_seen(user_email, job["url"]):
            new_jobs.append(job)
            mark_job_as_seen(user_email, job["url"], job["title"], job["company"])
    return new_jobs

def get_user_job_count(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM seen_jobs WHERE user_email = ?",
        (user_email,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count

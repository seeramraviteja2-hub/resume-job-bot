
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



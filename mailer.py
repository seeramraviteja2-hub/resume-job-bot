# ─────────────────────────────────────────────
#  mailer.py
#  Formats and sends new job listings to the student's email
#  Credentials are passed in from the UI — no .env needed
# ─────────────────────────────────────────────
 
import smtplib
from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart
 
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
 
 
def build_email_body(jobs: list[dict], keywords: list[str]) -> str:
    """Creates a clean HTML email listing all new jobs."""
    keyword_str = ", ".join(keywords[:5])
 
    rows = ""
    for i, job in enumerate(jobs, start=1):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        rows += f"""
        <tr style="background-color:{bg};">
            <td style="padding:10px;border:1px solid #ddd;">{i}</td>
            <td style="padding:10px;border:1px solid #ddd;">{job['title']}</td>
            <td style="padding:10px;border:1px solid #ddd;">{job['company']}</td>
            <td style="padding:10px;border:1px solid #ddd;">{job['source']}</td>
            <td style="padding:10px;border:1px solid #ddd;">
                <a href="{job['url']}" style="color:#1a73e8;">View Job</a>
            </td>
        </tr>
        """
 
    return f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:800px;margin:auto;">
        <h2 style="color:#1a73e8;">🎯 New Job Matches Found!</h2>
        <p>Here are <strong>{len(jobs)} new job(s)</strong> based on your resume keywords:</p>
        <p><strong>Keywords used:</strong> {keyword_str}</p>
        <table style="width:100%;border-collapse:collapse;margin-top:20px;">
            <thead>
                <tr style="background-color:#1a73e8;color:white;">
                    <th style="padding:10px;text-align:left;">#</th>
                    <th style="padding:10px;text-align:left;">Job Title</th>
                    <th style="padding:10px;text-align:left;">Company</th>
                    <th style="padding:10px;text-align:left;">Source</th>
                    <th style="padding:10px;text-align:left;">Link</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:30px;color:#888;font-size:12px;">
            Sent by Resume Job Bot — only new jobs you haven't seen before.
        </p>
    </body></html>
    """
 
 
def send_jobs_email(
    to_email:        str,
    jobs:            list[dict],
    keywords:        list[str],
    sender_email:    str,
    sender_password: str,
) -> bool:
    """
    Sends the job listings email to the student.
    Credentials come from the Streamlit UI — no .env file needed.
    Returns True if sent successfully, False otherwise.
    """
    if not jobs:
        print("[Email] No jobs to send.")
        return False
 
    message = MIMEMultipart("alternative")
    message["Subject"] = f"🎯 {len(jobs)} New Job Match(es) Found for You!"
    message["From"]    = sender_email
    message["To"]      = to_email
    message.attach(MIMEText(build_email_body(jobs, keywords), "html"))
 
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
 
        print(f"[Email] Sent successfully to {to_email}")
        return True
 
    except smtplib.SMTPAuthenticationError:
        print("[Email] Auth failed — wrong Gmail or App Password.")
        return False
 
    except Exception as e:
        print(f"[Email] Error: {e}")
        return False
 

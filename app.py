# ─────────────────────────────────────────────
#  app.py
#  Main Streamlit app — the UI that ties everything together
#  Run with: py -m streamlit run app.py
# ─────────────────────────────────────────────
 
import streamlit as st
from resume_parser import parse_resume
from job_scraper   import run_scraper
from database      import create_tables, filter_new_jobs, get_user_job_count
from mailer        import send_jobs_email
 
 
# ── App Setup ────────────────────────────────────────────────────────────────
 
st.set_page_config(
    page_title = "Resume Job Bot",
    page_icon  = "🎯",
    layout     = "centered",
)
 
create_tables()
 
 
# ── Page Header ──────────────────────────────────────────────────────────────
 
st.title("🎯 Resume Job Bot")
st.markdown(
    "Upload your resume → we extract your skills → "
    "we find **new** jobs on Naukri & Indeed → we email them to you!"
)
st.divider()
 
 
# ── Step 1: User Inputs ──────────────────────────────────────────────────────
 
st.subheader("Step 1 — Your Details")
 
user_email   = st.text_input("📧 Your Email Address (where we'll send jobs)", placeholder="you@example.com")
uploaded_pdf = st.file_uploader("📄 Upload Your Resume (PDF only)", type=["pdf"])
 
 
# ── Email Sender Credentials (entered in UI, not .env) ───────────────────────
 
with st.expander("⚙️ Email Sender Settings (click to set up once)"):
    st.markdown(
        "We send job alerts from a Gmail account. "
        "Enter **any Gmail** you own + its App Password below. "
        "This is **not stored anywhere** — only used for this session."
    )
    sender_email = st.text_input(
        "📤 Sender Gmail Address",
        placeholder="yourgmail@gmail.com",
    )
    sender_password = st.text_input(
        "🔑 Gmail App Password",
        type="password",
        placeholder="xxxx xxxx xxxx xxxx",
    )
    st.caption(
        "💡 App Password ≠ your normal Gmail password. "
        "Get one free at myaccount.google.com/apppasswords "
        "(requires 2-Step Verification to be on)."
    )
 
 
# ── Step 2: Parse Resume ──────────────────────────────────────────────────────
 
if uploaded_pdf:
    st.subheader("Step 2 — Keywords Extracted from Your Resume")
 
    with st.spinner("Reading your resume..."):
        parsed = parse_resume(uploaded_pdf)
 
    keywords = parsed["keywords"]
 
    if keywords:
        st.success(f"✅ Found **{len(keywords)}** skill keywords in your resume!")
        st.markdown("  ".join([f"`{kw}`" for kw in keywords]))
 
        with st.expander("📃 View extracted resume text"):
            st.text(parsed["raw_text"][:3000])
    else:
        st.warning("⚠️ No skill keywords found. Make sure your resume has skills like Python, SQL, React etc.")
        st.stop()
 
    st.divider()
 
 
# ── Step 3: Find Jobs ─────────────────────────────────────────────────────────
 
    st.subheader("Step 3 — Find New Jobs")
 
    if user_email:
        past_count = get_user_job_count(user_email)
        if past_count > 0:
            st.info(f"📊 We've already found **{past_count}** jobs for you before. Only new ones will appear!")
 
    find_button = st.button("🔍 Find Jobs Now", type="primary", use_container_width=True)
 
    if find_button:
 
        if not user_email or "@" not in user_email:
            st.error("❌ Please enter a valid email address.")
            st.stop()
 
        if not sender_email or not sender_password:
            st.error("❌ Please open '⚙️ Email Sender Settings' above and fill in your Gmail + App Password.")
            st.stop()
 
        with st.spinner("🤖 Searching Naukri & Indeed... (takes ~30 seconds)"):
            all_scraped_jobs = run_scraper(keywords)
 
        if not all_scraped_jobs:
            st.error("😕 No jobs found. Job sites may have updated their layout. Try again later.")
            st.stop()
 
        st.success(f"🔎 Found **{len(all_scraped_jobs)}** total jobs.")
 
        with st.spinner("🧹 Filtering jobs you've already seen..."):
            new_jobs = filter_new_jobs(user_email, all_scraped_jobs)
 
        if not new_jobs:
            st.info("✅ No new jobs this time — all were ones you've already seen. Check back later!")
            st.stop()
 
        st.success(f"🎉 **{len(new_jobs)} new job(s)** found!")
 
 
# ── Step 4: Show Results ──────────────────────────────────────────────────────
 
        st.subheader("Step 4 — Your New Job Matches")
 
        for i, job in enumerate(new_jobs, start=1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{i}. {job['title']}**")
                st.markdown(f"🏢 {job['company']}")
            with col2:
                st.markdown(f"🌐 `{job['source']}`")
                st.markdown(f"[View Job ↗]({job['url']})")
            st.divider()
 
 
# ── Step 5: Send Email ────────────────────────────────────────────────────────
 
        st.subheader("Step 5 — Email Results")
 
        with st.spinner(f"📧 Sending {len(new_jobs)} jobs to {user_email}..."):
            email_sent = send_jobs_email(
                to_email        = user_email,
                jobs            = new_jobs,
                keywords        = keywords,
                sender_email    = sender_email,
                sender_password = sender_password,
            )
 
        if email_sent:
            st.success(f"✅ Email sent to **{user_email}**! Check your inbox.")
        else:
            st.error(
                "❌ Email failed. Double-check your Sender Gmail and App Password. "
                "Make sure 2-Step Verification is enabled on that Google account."
            )
 
else:
    st.info("👆 Upload your resume above to get started.")
# 🎯 Resume Job Bot

Upload your resume → extract skill keywords → find new jobs on Naukri & Indeed → get them in your email!

---

## 🗂️ Project Structure

```
resume-job-bot/
├── app.py              # Streamlit UI — main entry point
├── resume_parser.py    # Extracts keywords from PDF resume
├── job_scraper.py      # Playwright automation for Naukri & Indeed
├── database.py         # SQLite — tracks seen jobs per user
├── email_sender.py     # Sends job email to the student
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── .gitignore
```

---

## ⚙️ Local Setup (Step by Step)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/resume-job-bot.git
cd resume-job-bot
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set up your .env file
```bash
cp .env.example .env
# Now open .env and fill in your Gmail + App Password
```

> **Gmail App Password**: Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> Make sure 2FA is enabled on your Google account first.

### 5. Run the app
```bash
streamlit run app.py
```

App will open at `http://localhost:8501` 🎉

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push your code to a **public GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → connect your GitHub repo → set `app.py` as the entry file
4. Under **"Advanced settings → Secrets"**, add your `.env` values:
   ```
   EMAIL_ADDRESS = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"
   ```
5. Click **Deploy** — done! ✅

> Note: Playwright on Streamlit Cloud needs `packages.txt`. See below.

### packages.txt (needed for Streamlit Cloud)
Create a file called `packages.txt` in the root with:
```
chromium
chromium-driver
```

---

## 🔒 Security Notes

- Never commit `.env` to GitHub — it's in `.gitignore`
- Use Gmail App Passwords, not your real password
- The SQLite database (`seen_jobs.db`) is local only

---

## 🧠 How It Works

1. **Resume Parsing** — `pdfplumber` extracts text from PDF, then regex matches against a skill keyword list
2. **Job Scraping** — `Playwright` opens a headless Chromium browser and scrapes Naukri & Indeed
3. **Deduplication** — Every job URL is stored in SQLite. Only URLs the user hasn't seen are returned
4. **Email** — Clean HTML email is sent via Gmail SMTP with all new job listings

---

## 📬 Contact

Built for learning purposes. Feel free to fork and improve!

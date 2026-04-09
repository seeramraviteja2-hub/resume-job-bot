# ─────────────────────────────────────────────
#  resume_parser.py
#  Reads a PDF resume and pulls out skill keywords
# ─────────────────────────────────────────────

import pdfplumber
import re


# ── Keywords we care about ──────────────────────────────────────────────────
# Add more skills here as needed. Keep it lowercase — we compare lowercase.
SKILL_KEYWORDS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "swift", "kotlin", "php", "r", "matlab", "scala",

    # Web & frameworks
    "react", "angular", "vue", "django", "flask", "fastapi", "spring",
    "node.js", "nodejs", "express", "html", "css", "tailwind",

    # Data & ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
    "data analysis", "data science", "sql", "mysql", "postgresql", "mongodb",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "github actions", "terraform", "linux", "bash",

    # Tools & others
    "git", "github", "jira", "agile", "scrum", "rest api", "graphql",
    "playwright", "selenium", "tableau", "power bi", "excel",

    # Job roles (useful for searching)
    "software engineer", "data engineer", "data scientist", "backend",
    "frontend", "full stack", "fullstack", "devops", "ml engineer",
    "product manager", "ui/ux", "qa engineer", "android", "ios",
]


def extract_text_from_pdf(pdf_file) -> str:
    """
    Takes a PDF file object (from Streamlit uploader)
    and returns all the text inside it as a single string.
    """
    full_text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

    return full_text.strip()


def extract_keywords(resume_text: str) -> list[str]:
    """
    Scans the resume text and returns a list of matching skill keywords.
    Simple and effective — no heavy NLP library needed.
    """
    resume_lower = resume_text.lower()
    found_keywords = []

    for skill in SKILL_KEYWORDS:
        # Use word boundary matching so "r" doesn't match inside "react"
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_lower):
            found_keywords.append(skill)

    # Remove duplicates and sort
    unique_keywords = sorted(set(found_keywords))
    return unique_keywords


def parse_resume(pdf_file) -> dict:
    """
    Main function — call this from app.py.
    Returns a dict with the raw text and extracted keywords.
    """
    raw_text = extract_text_from_pdf(pdf_file)
    keywords  = extract_keywords(raw_text)

    return {
        "raw_text": raw_text,
        "keywords": keywords,
    }

import re
import nltk
import pdfplumber
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")
nltk.download("stopwords")

from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))

# ---------- CLEAN TEXT ----------
def clean_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    words = text.split()

    words = [w for w in words if w not in stop_words]

    return " ".join(words)


# ---------- EXTRACT TEXT FROM PDF ----------
def extract_text_from_pdf(file):

    text = ""

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:   # avoid None
                    text += page_text + "\n"

    except Exception as e:

        print("PDF extraction error:", e)

    return text


# ---------- SKILL DATABASE ----------
skills_db = [
    # Programming
    "python","java","c++","c","c#",

    # Web
    "html","css","javascript","react","angular","vue",
    "node","flask","django","spring","spring boot",

    # Data
    "machine learning","deep learning","data science",
    "data analysis","numpy","pandas","matplotlib",
    "tensorflow","pytorch","nlp","power bi","tableau",

    # Database
    "sql","mysql","postgresql","mongodb","oracle",

    # Tools
    "git","github","docker","kubernetes","aws","azure","gcp",

    # Others
    "linux","rest api","microservices","excel"
]


# ---------- EXTRACT SKILLS ----------
def extract_skills(text):
    
    found_skills = []

    text = text.lower()

    for skill in skills_db:

        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.append(skill)

    return list(set(found_skills))


# ---------- MATCH SCORE ----------
def calculate_match(resume, job_desc):
    
    if not resume or not job_desc:
        return 0

    cv = CountVectorizer(stop_words="english")

    matrix = cv.fit_transform([resume, job_desc])

    similarity = cosine_similarity(matrix)[0][1]

    score = similarity * 100

    # Ensure score is not extremely small
    if score < 5:
        score = 5

    return round(score, 2)

# ---------- SKILL GAP ----------
def skill_gap(resume_skills, job_skills):

    matched = list(set(resume_skills) & set(job_skills))

    missing = list(set(job_skills) - set(resume_skills))

    return matched, missing


# ---------- COURSE RECOMMENDATION ----------
def recommend_courses(missing):
    
    course_links = {
        "python":"https://www.coursera.org/learn/python",
        "machine learning":"https://www.coursera.org/learn/machine-learning",
        "sql":"https://www.coursera.org/learn/sql-for-data-science",
        "node":"https://www.udemy.com/course/nodejs-express-mongodb-bootcamp",
        "javascript":"https://www.freecodecamp.org/learn/javascript",
        "react":"https://www.udemy.com/course/react-the-complete-guide",
        "docker":"https://www.udemy.com/course/docker-mastery",
        "aws":"https://www.coursera.org/learn/aws-fundamentals",
        "git":"https://www.freecodecamp.org/news/learn-git",
        "linux":"https://www.udemy.com/course/linux-mastery"
    }

    rec = {}

    for skill in missing:

        skill_lower = skill.lower()

        # If we have specific course
        if skill_lower in course_links:
            rec[skill] = course_links[skill_lower]

        # If not found, give generic search link
        else:
            rec[skill] = f"https://www.coursera.org/search?query={skill_lower}"

    return rec
def resume_suggestions(resume_text, missing_skills):
    
    suggestions = []

    # Resume length check
    if len(resume_text.split()) < 150:
        suggestions.append("Your resume is short. Add more details about projects, internships, and achievements.")

    # Missing skills suggestion
    if missing_skills:
        suggestions.append("Consider adding these important skills mentioned in the job description: " + ", ".join(missing_skills))

    # Projects suggestion
    if "project" not in resume_text.lower():
        suggestions.append("Add a projects section to demonstrate practical experience.")

    # Certifications suggestion
    if "certification" not in resume_text.lower():
        suggestions.append("Include certifications related to the job role.")

    # Experience suggestion
    if "experience" not in resume_text.lower():
        suggestions.append("Mention internships or work experience to strengthen your resume.")

    # Skills suggestion
    if "skills" not in resume_text.lower():
        suggestions.append("Add a clear Skills section for ATS systems.")

    return suggestions
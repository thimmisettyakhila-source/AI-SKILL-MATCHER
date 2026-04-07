import streamlit as st
import sqlite3
import io
import pdfplumber
import pandas as pd

from auth import create_user_table, register_user, login_user
from nlp_utils import clean_text, extract_skills, calculate_match, skill_gap, recommend_courses, resume_suggestions
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ---------------- PAGE CONFIG ----------------

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")


# ---------------- PDF TEXT EXTRACTION ----------------

def extract_text_from_pdf(file):

    text = ""

    file.seek(0)

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# ---------------- DATABASE ----------------

create_user_table()

def create_resume_table():

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    match_score REAL
    )
    """)

    conn.commit()
    conn.close()

create_resume_table()


def save_result(username,score):

    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO resumes(username,match_score) VALUES(?,?)",
    (username,score)
    )

    conn.commit()
    conn.close()


# ---------------- PDF REPORT ----------------

def generate_pdf(username,score,matched,missing):

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer)

    elements = []

    elements.append(Paragraph("Resume Match Report",styles['Title']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"User : {username}",styles['Normal']))
    elements.append(Paragraph(f"Match Score : {score}%",styles['Normal']))

    elements.append(Spacer(1,20))

    elements.append(Paragraph("Matched Skills",styles['Heading2']))

    for s in matched:
        elements.append(Paragraph(s,styles['Normal']))

    elements.append(Spacer(1,20))

    elements.append(Paragraph("Missing Skills",styles['Heading2']))

    for s in missing:
        elements.append(Paragraph(s,styles['Normal']))

    doc.build(elements)

    buffer.seek(0)

    return buffer
def display_skills(title, skills, color):
    st.markdown(f"### {title}")

    if not skills:
        st.info("No skills found.")
        return

    cols = st.columns(3)

    for index, skill in enumerate(skills):
        with cols[index % 3]:
            st.markdown(
                f"""
                <div style="
                    background-color:{color};
                    padding:10px;
                    border-radius:10px;
                    text-align:center;
                    color:white;
                    font-weight:500;
                    margin-bottom:10px;">
                    {skill}
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""


# ---------------- LOGIN PAGE ----------------

def login_page():

    st.title("AI Resume Analyzer Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        user = login_user(username,password)

        if user:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

        else:
            st.error("Invalid Credentials")

    if st.button("Create Account"):
        st.session_state.page="register"
        st.rerun()


# ---------------- REGISTER PAGE ----------------

def register_page():

    st.title("Register")

    username = st.text_input("Create Username")
    password = st.text_input("Create Password",type="password")
    confirm = st.text_input("Confirm Password",type="password")

    if st.button("Register"):

        if password != confirm:
            st.error("Passwords do not match")

        else:

            if register_user(username,password):
                st.success("Registration Successful")

            else:
                st.error("Username already exists")

    if st.button("Back to Login"):
        st.session_state.page="login"
        st.rerun()


# ---------------- DASHBOARD ----------------

def dashboard():

    st.sidebar.title("Resume Analyzer")

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard","Compare Resumes","Match History","About"]
    )

    st.sidebar.success(st.session_state.username)

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()


# ---------------- DASHBOARD PAGE ----------------

    if menu == "Dashboard":

        st.title("AI Resume Matching System")

        col1,col2 = st.columns(2)

# ---------- RESUME ----------

        with col1:

            st.subheader("Resume")

            resume_option = st.radio(
                "Resume Input",
                ["Upload PDF","Paste Text"]
            )

            if resume_option == "Upload PDF":

                resume_file = st.file_uploader(
                    "Upload Resume",
                    type=["pdf"]
                )

                if resume_file is not None:

                    st.session_state.resume_text = extract_text_from_pdf(resume_file)

                    st.success("Resume uploaded successfully")

            else:

                st.session_state.resume_text = st.text_area(
                    "Paste Resume",
                    value=st.session_state.resume_text,
                    height=200
                )


# ---------- JOB DESCRIPTION ----------

        with col2:

            st.subheader("Job Description")

            jd_option = st.radio(
                "JD Input",
                ["Upload PDF","Paste Text"]
            )

            if jd_option == "Upload PDF":

                jd_file = st.file_uploader(
                    "Upload JD",
                    type=["pdf"]
                )

                if jd_file is not None:

                    st.session_state.job_desc = extract_text_from_pdf(jd_file)

                    st.success("Job Description uploaded successfully")

            else:

                st.session_state.job_desc = st.text_area(
                    "Paste Job Description",
                    value=st.session_state.job_desc,
                    height=200
                )


# ---------- ANALYZE ----------

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing Resume... Please wait"):

                if st.session_state.resume_text and st.session_state.job_desc:
                    # ---------- SHOW EXTRACTED TEXT ----------

                    st.subheader("Extracted Resume & Job Description")

                    with st.expander("View Extracted Resume"):
                        st.text_area(
                            "Resume Content",
                            value=st.session_state.resume_text,
                            height=250
                        )

                    with st.expander("View Extracted Job Description"):
                        st.text_area(
                            "Job Description Content",
                            value=st.session_state.job_desc,
                            height=250
                        )

                    clean_resume = clean_text(st.session_state.resume_text)
                    clean_job = clean_text(st.session_state.job_desc)

                    score = calculate_match(clean_resume,clean_job)

                    st.subheader("Match Score")

                    c1,c2 = st.columns(2)

                    with c1:
                        st.metric("Resume Match",f"{score}%")
                        st.progress(int(score)/100)

                    with c2:
                        ats = round(score*0.9,2)
                        st.metric("ATS Compatibility",f"{ats}%")
                        st.progress(int(score)/100)

# ---------- Resume Strength ----------

                    if score >= 80:
                        st.success("Excellent Resume Match")

                    elif score >= 60:
                        st.info("Good Resume Match")

                    elif score >= 40:
                        st.warning("Average Match — Improve Skills")

                    else:
                        st.error("Low Match — Resume needs improvement")


                    st.subheader("Skills Analysis")
                    resume_skills = extract_skills(clean_resume)
                    job_skills = extract_skills(clean_job)

                    matched, missing = skill_gap(resume_skills, job_skills)

                    col1, col2 = st.columns(2)

                    with col1:
                        display_skills("Resume Skills", resume_skills, "#1f77b4")

                    with col2:
                        display_skills("Job Skills", job_skills, "#ff7f0e")

                    st.divider()

                    col3, col4 = st.columns(2)

                    with col3:
                        display_skills("Matched Skills", matched, "#2ca02c")

                    with col4:
                        display_skills("Missing Skills", missing, "#d62728")


# ---------- Courses ----------

                    st.subheader("Recommended Courses")

                    courses = recommend_courses(missing)

                    for skill,link in courses.items():
                        st.markdown(f"**{skill}** → {link}")


# ---------- Suggestions ----------

                    st.subheader("Resume Improvement Suggestions")

                    suggestions = resume_suggestions(st.session_state.resume_text,missing)

                    for s in suggestions:
                        st.info(s)


# ---------- Save Result ----------

                    save_result(st.session_state.username,score)


# ---------- PDF ----------

                    pdf = generate_pdf(
                        st.session_state.username,
                        score,
                        matched,
                        missing
                    )

                    st.download_button(
                        "Download Report",
                        pdf,
                        "resume_report.pdf"
                    )

                else:

                    st.warning("Upload Resume and Job Description")

    elif menu == "Compare Resumes":
    
        st.title("Compare Multiple Resumes")

        uploaded_files = st.file_uploader(
            "Upload Multiple Resumes",
            type=["pdf"],
            accept_multiple_files=True
        )
        jd_text = st.text_area("Paste Job Description")

        if st.button("Compare Now"):

            if uploaded_files and jd_text:

                results = []

                clean_jd = clean_text(jd_text)

                for file in uploaded_files:

                    resume_text = extract_text_from_pdf(file)
                    clean_resume = clean_text(resume_text)

                    score = calculate_match(clean_resume, clean_jd)

                    results.append({
                        "Resume Name": file.name,
                        "Score (%)": score
                    })

                df = pd.DataFrame(results)

                df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
                df.index=df.index+1

                st.subheader("Resume Ranking")
                st.dataframe(df)

        
                best = df.iloc[0]

                st.success(f"Best Resume: {best['Resume Name']} ({best['Score (%)']}%)")

            else:
                st.warning("Please upload resumes and paste job description")
# ---------------- HISTORY ----------------

    elif menu == "Match History":

        st.title("Previous Results")

        conn = sqlite3.connect("resumes.db")
        cursor = conn.cursor()

        cursor.execute("SELECT username,match_score FROM resumes")

        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=["Username", "Match Score (%)"])

        st.table(df)

        conn.close()


# ---------------- ABOUT ----------------

    elif menu == "About":

        st.title("About Project")

        st.write("""
AI Resume Matching System

Features
- Resume Parsing
- Job Matching
- Compare Resumes
- Skill Gap Detection
- ATS Score
- Course Recommendation
- PDF Report
""")


# ---------------- PAGE CONTROL ----------------

if not st.session_state.logged_in:

    if st.session_state.page == "login":
        login_page()
    else:
        register_page()

else:
    dashboard()

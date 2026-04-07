📄 AI Resume Analyzer & Matcher

An intelligent web application built using Streamlit that analyzes resumes, compares them with job descriptions, and provides insights like match score, skill gaps, and recommendations.


🚀 Features
      🔹 Resume Analysis
            -->Upload resume (PDF) or paste text
            -->Upload job description or paste text
            -->Calculates Resume Match Score
            -->Displays ATS Compatibility Score
      🔹 Skill Analysis
            -->Extracts skills from resume & job description
            Shows:
            -->Matched Skills
            -->Missing Skills
      🔹 Recommendations
            -->Suggests courses for missing skills
            -->Provides resume improvement tips
      🔹 PDF Report
            -->Download complete analysis report as PDF
      🔹 Match History
            -->Stores previous results using SQLite database
      🔹 Compare Multiple Resumes
            -->Upload multiple resumes
            -->Compare them against one job description
            -->Displays ranking of resumes
            -->Highlights the best resume


🛠️ Tech Stack
       Frontend: Streamlit
       Backend: Python
       Database: SQLite
       Libraries:
           -->pdfplumber (PDF extraction)
           -->nltk (text processing)
           -->scikit-learn (similarity calculation)
           -->pandas (data handling)
           -->reportlab (PDF generation)


📂 Project Structure
       resume_matcher_project/
      │
      ├── app.py                # Main Streamlit application
      ├── nlp_utils.py         # NLP processing & logic
      ├── auth.py              # Login & registration system
      ├── resumes.db           # SQLite database
      ├── requirements.txt     # Required libraries
      └── README.md            # Project documentation


⚙️ Installation & Setup
        1.Clone the repository
             git clone https://github.com/thimmisettyakhila-source/AI-SKILL-MATCHER.git cd resume-analyzer
        2.Install dependencies
             pip install -r requirements.txt
        3.Run the application
             python -m streamlit run app.py


📊 How It Works
     1.Extracts text from resume & job description
     2.Cleans text using NLP techniques
     3.Calculates similarity using Cosine Similarity
     4.Identifies skill gaps using predefined skill database
     5.Generates insights and recommendations

📸 Screenshots
      

https://github.com/user-attachments/assets/4d16d265-ad91-4cab-8139-4b877edd7240



👩‍💻 Author
     Akhila Thimmisetty
         ==> Aspiring Software Developer
         ==> Skills: Python, Web Development, AI/ML


⭐ If you like this project

Give it a ⭐ on GitHub and share with others!

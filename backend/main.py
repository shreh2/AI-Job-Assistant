from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import pdfplumber
import docx
import spacy
import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import re  # <-- This is required for using `re.search()`



# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load NLP model
nlp = spacy.load("en_core_web_sm")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### 📌 Helper Functions ###
def extract_text(file: UploadFile):
    """Extract text from PDF or DOCX file properly handling FastAPI's UploadFile."""
    file_content = file.file.read()
    file.file.seek(0)

    if file.filename.endswith(".pdf"):
        with pdfplumber.open(file.file) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return None

def extract_keywords(text):
    """Extract keywords from resume using NLP."""
    doc = nlp(text)
    return list(set(token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]))

def generate_questions(job_description, resume_text):
    """Generate structured interview questions without hardcoding language."""
    
    prompt = f"""
    You are an AI assistant trained to generate structured and well-formatted interview questions. 
    Your task is to generate **exactly 3 interview questions per category**, ensuring each category is distinct.

    **Guidelines:**
    - Carefully analyze the **resume** and **job description** to determine relevant technologies and skills.
    - **Create a separate section for "Coding Questions"**, where you ask **three different coding problems**.
    -  sed on the job description and resume.

    **Job Description:**
    {job_description}
    
    **Resume:**
    {resume_text}
    
    **Response Format:** (Follow this exactly)
    
    **Target Company Role Specific:**
    1. Question about the specific role at the company.
    2. Technical question based on resume skills.
    3. Coding question in the most relevant programming language.

    **Similar Role in Other Companies:**
    1. Common question from other companies hiring for this role.
    2. Another technical question based on resume.
    3. Another coding question in a relevant language.

    **Behavioral Questions:**
    1. Tell me about a time when you faced a major challenge in your role.
    2. Give an example of when you used data to influence a key business decision.
    3. How do you handle conflicts in cross-functional teams?

    **Coding Questions:**
    1. Generate a coding challenge relevant to the job description.
    2. Generate a second coding question that tests SQL skills.
    3. Generate a third SQL coding question which should be harder than the previous

    **Now generate the questions in the exact format above.**
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    questions_text = response.choices[0].message.content.strip()

    # Extract sections using regex
    def extract_section(header, text):
        pattern = rf"\*\*{header}:\*\*(.*?)(?=\*\*|$)"
        match = re.search(pattern, text, re.DOTALL)
        return [q.strip() for q in match.group(1).split("\n") if q.strip()] if match else []

    target_company_role = extract_section("Target Company Role Specific", questions_text)
    similar_role_other_companies = extract_section("Similar Role in Other Companies", questions_text)
    behavioral_questions = extract_section("Behavioral Questions", questions_text)
    coding_questions = extract_section("Coding Questions", questions_text)

    return {
        "target_company_role": target_company_role[:3],
        "similar_role_in_other_companies": similar_role_other_companies[:3],
        "behavioral_questions": behavioral_questions[:3],
        "coding_questions": coding_questions[:3]
    }

### 📌 API Endpoints ###

# Analyze Resume API
@app.post("/analyze_resume/")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Analyze resume match score using OpenAI for better relevance."""

    resume_text = extract_text(file)
    if not resume_text:
        return {"error": "Invalid file format"}

    # Prompt OpenAI GPT model to analyze relevance
    # Prompt OpenAI GPT model to analyze relevance
    prompt = f"""
    You are an AI assistant evaluating how well a candidate's resume matches a job description.
    Consider skills, technologies, relevant experience, and project domain.

    **Job Description:**
    {job_description}

    **Resume:**
    {resume_text}

    **Task:**
    - Compare the resume with the job description.
    - Identify missing relevant skills, technologies, and domain expertise.
    - Suggest specific changes to improve the match.
    - Highlight suggested changes by wrapping them in <mark> tags (to show in green).

    **Response Format:**
    Match Score: (number between 0-100)
    Explanation: (brief reason for score)
    Suggested Resume: (resume text with improvements wrapped in [[highlight]] tags)
    """

    # Call OpenAI API synchronously
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    # Extract match score, explanation, and suggested resume
    gpt_response = response.choices[0].message.content.strip()

    match_score = None
    explanation = "No explanation provided."
    suggested_resume = resume_text  # Default to original resume if parsing fails

    for line in gpt_response.split("\n"):
        if line.startswith("Match Score:"):
            try:
                match_score = float(line.split(":")[1].strip())
            except ValueError:
                match_score = 0  # Default if parsing fails
        elif line.startswith("Explanation:"):
            explanation = line.split(":", 1)[1].strip()
        elif line.startswith("Suggested Resume:"):
            suggested_resume = "\n".join(gpt_response.split("Suggested Resume:")[1:]).strip()

    # Ensure valid score
    if match_score is None or match_score < 0 or match_score > 100:
        match_score = 0  # Default if parsing fails

    return {
        "match_score": round(match_score, 2),
        "explanation": explanation,
        "optimized_resume": suggested_resume
    }

# Generate CV API
@app.post("/generate_cv/")
async def generate_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    custom_keywords: str = Form("")
):
    """Generate a Cover Letter based on the resume and job description."""
    
    resume_text = extract_text(file)
    if not resume_text:
        return {"error": "Invalid file format"}

    cv_prompt = f"Write a cover letter based on the industry standards including experience and skills from the resume and matching them to the job description:\n\n{resume_text}\n\nCustom Keywords: {custom_keywords}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": cv_prompt}]
    )
    optimized_resume = response.choices[0].message.content

    return {"optimized_resume": optimized_resume}

# Generate Questions API
@app.post("/generate_questions/")
async def generate_questions_api(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Generate interview questions based on resume & job description."""
    
    resume_text = extract_text(file)
    if not resume_text:
        return {"error": "Invalid file format"}
    
    questions = generate_questions(job_description, resume_text)
    
    return questions

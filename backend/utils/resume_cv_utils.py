import pdfplumber
import docx
from sentence_transformers import SentenceTransformer, util
import spacy
import openai

# Load NLP model
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

# OpenAI API Key (Ensure it's set in your environment)
OPENAI_API_KEY = "your_openai_api_key"

### 📌 Resume Analyzer
def extract_text_from_pdf(file):
    with pdfplumber.open(file.file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_keywords(text):
    doc = nlp(text)
    return list(set(token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]))

def calculate_similarity(resume_text, job_description):
    embeddings1 = model.encode(resume_text, convert_to_tensor=True)
    embeddings2 = model.encode(job_description, convert_to_tensor=True)
    return util.pytorch_cos_sim(embeddings1, embeddings2).item() * 100

def analyze_resume(file, job_description):
    # Extract text
    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file)
    elif file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(file)
    else:
        return {"error": "Unsupported file format"}

    # Extract keywords & match score
    keywords = extract_keywords(resume_text)
    match_score = calculate_similarity(resume_text, job_description)

    return {
        "match_score": round(match_score, 2),
        "resume_keywords": keywords,
        "suggestion": "Consider adding missing skills from the job description."
    }

### 📌 CV & Cover Letter Generator
def generate_resume_cover_letter(file, job_description, custom_keywords):
    resume_text = extract_text_from_pdf(file) if file.filename.endswith(".pdf") else extract_text_from_docx(file)
    
    # Generate CV using OpenAI
    prompt = f"Rewrite the following resume to match the job description:\n\nJob Description: {job_description}\n\nCustom Keywords: {custom_keywords}\n\nResume:\n{resume_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )
    optimized_resume = response["choices"][0]["message"]["content"]

    # Generate Cover Letter
    prompt_cover_letter = f"Write a professional cover letter for the job:\n\nJob Description: {job_description}\n\nResume:\n{optimized_resume}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt_cover_letter}]
    )
    cover_letter = response["choices"][0]["message"]["content"]

    return {
        "optimized_resume": optimized_resume,
        "cover_letter": cover_letter
    }

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from backend.utils.resume_utils import analyze_resume
from backend.utils.cv_utils import generate_resume_cover_letter
from backend.utils.question_utils import generate_interview_questions
import uvicorn

app = FastAPI()

# Request model for resume & question generation
class JobRequest(BaseModel):
    job_description: str
    custom_keywords: str = ""

@app.post("/analyze_resume/")
async def analyze_resume_endpoint(file: UploadFile = File(...), job_description: str = Form(...)):
    result = await analyze_resume(file, job_description)
    return result

@app.post("/generate_cv/")
async def generate_cv_endpoint(request: JobRequest, file: UploadFile = File(...)):
    result = await generate_resume_cover_letter(file, request.job_description, request.custom_keywords)
    return result

@app.post("/generate_questions/")
async def generate_questions_endpoint(request: JobRequest):
    result = generate_interview_questions(request.job_description)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_ai_text(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert resume and cover letter writer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

async def generate_resume_cover_letter(file, job_description, custom_keywords):
    file_extension = file.filename.split(".")[-1]
    
    if file_extension == "pdf":
        resume_text = await extract_text_from_pdf(file)
    elif file_extension == "docx":
        resume_text = await extract_text_from_docx(file)
    else:
        return {"error": "Unsupported file format. Upload a PDF or DOCX file."}

    resume_prompt = f"Optimize this resume based on the job description:\n{job_description}\nResume:\n{resume_text}"
    optimized_resume = await generate_ai_text(resume_prompt)

    cover_letter_prompt = f"Generate a cover letter for this job:\n{job_description}\nInclude: {custom_keywords}"
    cover_letter = await generate_ai_text(cover_letter_prompt)

    return {"optimized_resume": optimized_resume, "cover_letter": cover_letter}

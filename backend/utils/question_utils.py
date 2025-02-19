import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_interview_questions(job_description):
    prompt = f"""
    Generate interview questions for the job description below:
    {job_description}

    Categories:
    1. Target Company-Specific Questions
    2. Similar Role at Other Companies
    3. Technology-Specific Questions
    4. General Role-Based Questions
    """

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI trained to generate technical and behavioral interview questions."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"interview_questions": response.choices[0].message.content.strip()}

# import os
# import openai
# import re

# # Load OpenAI API Key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Initialize OpenAI client
# client = openai.Client()

# def generate_questions(job_description, resume_text):
#     """Generate structured interview questions without hardcoding language."""
    
#     prompt = f"""
#     You are an AI assistant trained to generate structured and well-formatted interview questions. 
#     Your task is to generate **exactly 3 interview questions per category**, ensuring each category is distinct.

#     **Guidelines:**
#     - Carefully analyze the **resume** and **job description** to determine relevant technologies and skills.
#     - **Create a separate section for "Coding Questions"**, where you ask **three different coding problems**.
#     - The coding questions should be in the most relevant programming language based on the job description and resume.

#     **Job Description:**
#     {job_description}
    
#     **Resume:**
#     {resume_text}
    
#     **Response Format:** (Follow this exactly)
    
#     **Target Company Role Specific:**
#     1. Question about the specific role at the company.
#     2. Technical question based on resume skills.
#     3. Coding question in the most relevant programming language.

#     **Similar Role in Other Companies:**
#     1. Common question from other companies hiring for this role.
#     2. Another technical question based on resume.
#     3. Another coding question in a relevant language.

#     **Behavioral Questions:**
#     1. Tell me about a time when you faced a major challenge in your role.
#     2. Give an example of when you used data to influence a key business decision.
#     3. How do you handle conflicts in cross-functional teams?

#     **Coding Questions:**
#     1. Generate a coding challenge relevant to the job description.
#     2. Generate a second coding question that tests algorithmic thinking.
#     3. Generate a third coding question covering data structures or problem-solving.

#     **Now generate the questions in the exact format above.**
#     """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "system", "content": prompt}]
#     )

#     questions_text = response.choices[0].message.content.strip()

#     # Extract sections using regex
#     def extract_section(header, text):
#         pattern = rf"\*\*{header}:\*\*(.*?)(?=\*\*|$)"
#         match = re.search(pattern, text, re.DOTALL)
#         return [q.strip() for q in match.group(1).split("\n") if q.strip()] if match else []

#     target_company_role = extract_section("Target Company Role Specific", questions_text)
#     similar_role_other_companies = extract_section("Similar Role in Other Companies", questions_text)
#     behavioral_questions = extract_section("Behavioral Questions", questions_text)
#     coding_questions = extract_section("Coding Questions", questions_text)

#     return {
#         "target_company_role": target_company_role[:3],
#         "similar_role_in_other_companies": similar_role_other_companies[:3],
#         "behavioral_questions": behavioral_questions[:3],
#         "coding_questions": coding_questions[:3]
#     }

# # Sample Test Data
# job_desc = """
# Job Description - SQL, Teradata, Data warehouse, Tableau, JIRA/TFS. Advanced proficiency in SQL for querying, data manipulation, and optimization.
# • Ability to write complex SQL queries, including subqueries, joins, window functions, and CTEs.
# • Experience with database management systems like Microsoft SQL Server, Teradata or Oracle.
# • Performance tuning and optimization of SQL queries and stored procedures.
# • Familiarity with ETL processes and data integration.
# • Strong skills in Tableau for creating interactive dashboards and visualizations.
# • Ability to connect Tableau to various data sources and build real-time, data-driven insights.
# • Proficiency in creating calculated fields, parameters, and leveraging Tableau's advanced visualization features.
# • Experience in designing user-friendly and visually appealing dashboards.
# """

# resume_text = """
# Developed and maintained over 10 analytical dashboards and 100+ performance metrics, providing insights to global AMZL teams and
# helping optimize delivery time and reduce operation costs.
# ● Leveraged Large Language Models (LLMs) on AWS to create a content classification tool for warehouse safety teams and improved
# their safety incident reporting accuracy by 65%.
# ● Built and automated data pipelines and data models using AWS (S3, Redshift, Lambda) to support data scientists and business leaders
# in generating critical business insights and maintaining data integrity.
# ● Improved org’s data operation efficiency by upgrading infrastructure frameworks and adopting best data practices and to improve
# accuracy reducing reporting time from hours to minutes.
# ● Mentored and trained new analysts, established best practices in SQL optimization, data integrity standards, and dashboard
# development, fostering a culture of continuous learning and improvement.
# """

# # Run the function and print results
# if __name__ == "__main__":
#     result = generate_questions(job_desc, resume_text)
#     print("\nGenerated Interview Questions:\n")
#     for category, questions in result.items():
#         print(f"{category.replace('_', ' ').title()}:\n")
#         for q in questions:
#             print(f"- {q}")
#         print("\n" + "="*50 + "\n")



from fastapi import FastAPI, UploadFile, File, Form
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_resume(job_description, resume_text):
    """Analyze resume match score and suggest improvements in green highlight."""

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
    Suggested Resume: (resume text with improvements wrapped in <mark> tags)
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

# Sample Test Data
job_description = """
Job Description - SQL, Teradata, Data warehouse, Tableau, JIRA/TFS. Advanced proficiency in SQL for querying, data manipulation, and optimization.
• Ability to write complex SQL queries, including subqueries, joins, window functions, and CTEs.
• Experience with database management systems like Microsoft SQL Server, Teradata or Oracle.
• Performance tuning and optimization of SQL queries and stored procedures.
• Familiarity with ETL processes and data integration.
• Strong skills in Tableau for creating interactive dashboards and visualizations.
• Ability to connect Tableau to various data sources and build real-time, data-driven insights.
• Proficiency in creating calculated fields, parameters, and leveraging Tableau's advanced visualization features.
• Experience in designing user-friendly and visually appealing dashboards.
"""

resume_text = """
Developed and maintained over 10 analytical dashboards and 100+ performance metrics, providing insights to global AMZL teams and
helping optimize delivery time and reduce operation costs.
● Leveraged Large Language Models (LLMs) on AWS to create a content classification tool for warehouse safety teams and improved
their safety incident reporting accuracy by 65%.
● Built and automated data pipelines and data models using AWS (S3, Redshift, Lambda) to support data scientists and business leaders
in generating critical business insights and maintaining data integrity.
● Improved org’s data operation efficiency by upgrading infrastructure frameworks and adopting best data practices and to improve
accuracy reducing reporting time from hours to minutes.
● Mentored and trained new analysts, established best practices in SQL optimization, data integrity standards, and dashboard
development, fostering a culture of continuous learning and improvement.
"""

if __name__ == "__main__":
    result = analyze_resume(job_description, resume_text)
    print(result)
const BASE_URL = "http://127.0.0.1:8000";  // ✅ Ensure this matches your backend URL

export async function analyzeResume(file, jobDescription, customKeywords) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);
    formData.append("custom_keywords", customKeywords);

    const response = await fetch(`${BASE_URL}/analyze_resume/`, {
        method: "POST",
        body: formData
    });

    return response.json();
}

export async function generateQuestions(file, jobDescription) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);

    const response = await fetch(`${BASE_URL}/generate_questions/`, {
        method: "POST",
        body: formData
    });

    return response.json();
}

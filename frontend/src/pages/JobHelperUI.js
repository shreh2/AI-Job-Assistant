import { useState } from "react";
import "./JobHelperUI.css";
import { saveAs } from 'file-saver'; // FileSaver library for downloading files

export default function JobHelperUI() {
    // State variables for storing input and results
    const [resume, setResume] = useState(null);
    const [jobDescription, setJobDescription] = useState("");
    const [customKeywords, setCustomKeywords] = useState("");
    const [analysisResult, setAnalysisResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [cvResult, setCvResult] = useState(null);
    const [questionsResult, setQuestionsResult] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [generatingCV, setGeneratingCV] = useState(false);
    const [generatingQuestions, setGeneratingQuestions] = useState(false);


    // Function to handle file upload
    const handleUpload = (event) => {
        setResume(event.target.files[0]);
    };


// Function to handle resume analysis
const handleAnalyze = async () => {
    if (!resume || !jobDescription) {
        alert("Please upload a resume and enter a job description.");
        return;
    }

    setAnalyzing(true);

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_description", jobDescription);
    formData.append("custom_keywords", customKeywords);

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze_resume/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Backend Response:", data);

        setAnalysisResult(data);

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch analysis results.");
    }

    setAnalyzing(false);
};

// Function to generate CV
const handleGenerateCV = async () => {
    if (!resume || !jobDescription) {
        alert("Please upload a resume and enter a job description.");
        return;
    }

    setGeneratingCV(true);

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_description", jobDescription);

    try {
        const response = await fetch("http://127.0.0.1:8000/generate_cv/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Generated CV Response:", data);

        setCvResult(data.optimized_resume);

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch CV results.");
    }

    setGeneratingCV(false);
};

// Function to generate interview questions
const handleGenerateQuestions = async () => {
    if (!resume || !jobDescription) {
        alert("Please upload a resume and enter a job description.");
        return;
    }

    setGeneratingQuestions(true);

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_description", jobDescription);

    try {
        const response = await fetch("http://127.0.0.1:8000/generate_questions/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Generated Questions Response:", data);

        setQuestionsResult(data);

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch interview questions.");
    }

    setGeneratingQuestions(false);
};

const getResultBoxClass = () => {
    if (analysisResult) return "result-box analyze-bg";
    if (cvResult) return "result-box cv-bg";
    if (questionsResult) return "result-box questions-bg";
    return "result-box";
};

// Function to replace [[highlight]] markers with styled spans
const formatHighlightedText = (text) => {
    if (!text) return "";
    return text.replace(/\[\[highlight\]\](.*?)\[\[\/highlight\]\]/g, '<span class="highlight">$1</span>');
};

// Function to download file
const downloadFile = (format) => {
    const textContent = analysisResult.optimized_resume;
    const blob = new Blob([textContent], { type: format === 'pdf' ? "application/pdf" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    saveAs(blob, `Optimized_Resume.${format}`);
};

    return (
        <div className="app-container">
            <h1 className="title">AI-Powered Job Helper</h1>

            {/* Upload Section */}

            {/* Upload Section */}
            {/* Upload Section */}
            <div className="upload-box">
                <label className="instruction-text">📂 Upload your resume (PDF or DOCX):</label>
                <input type="file" onChange={handleUpload} className="file-input" />
            </div>

            {/* Job Description Section */}
            <div className="job-description-box">
                <label className="instruction-text">📄 Paste Job Description:</label>
                <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    className="text-input"
                />
            </div>


            <div className="upload-container">

                {/* Buttons for each functionality */}
                <div className="button-container">
                    <button onClick={handleAnalyze} disabled={analyzing} className="action-button analyze-button">
                        {analyzing ? "Analyzing..." : "Analyze Resume"}
                    </button>
                    <button onClick={handleGenerateCV} disabled={generatingCV} className="action-button cv-button">
                        {generatingCV ? "Generating CV..." : "Generate CV"}
                    </button>
                    <button onClick={handleGenerateQuestions} disabled={generatingQuestions} className="action-button questions-button">
                        {generatingQuestions ? "Generating Questions..." : "Generate Practice Questions"}
                    </button>
                </div>
            </div>


            {/* Results Section */}
            {analysisResult && (
                <div className={`results-container analyze-bg`}>
                    {/* Left Section: Match Score & Optimized Resume */}
                    <div className="result-box left">
                        <h2 className="match-score" style={{ color: analysisResult.match_score >= 75 ? "#28a745" : "#dc3545" }}>
                            Match Score: {analysisResult.match_score}%
                        </h2>

                        <p className="match-explanation">{analysisResult.explanation}</p>

                        <h3>Optimized Resume</h3>
                        <pre className="content-box" dangerouslySetInnerHTML={{ __html: formatHighlightedText(analysisResult.optimized_resume) }} />

                        {/* Download Buttons */}
                        <div className="download-buttons">
                            <button className="download-button" onClick={() => downloadFile('docx')}>Download as Word</button>
                            <button className="download-button" onClick={() => downloadFile('pdf')}>Download as PDF</button>
                        </div>
                    </div>
                </div>
            )}


            {cvResult && (
                <div className={`results-container cv-bg`}>
                    {/* Center Section: Generated CV */}
                    <div className="result-box center">
                        <h3>AI Generated CV</h3>
                        <pre className="content-box">{cvResult}</pre>
                    </div>
                </div>
            )}

            {questionsResult && (
                <div className={`results-container questions-bg`}>
                    {/* Interview Questions */}
                    <div className="result-box right">
                        <h3>Sample Interview Questions</h3>
                        <div className="content-box">
                            <div className="question-category">Role-Specific Questions</div>
                            <ul>
                                {questionsResult.target_company_role.map((q, index) => <li key={index}>{q}</li>)}
                            </ul>

                            <div className="question-category">Other Companies</div>
                            <ul>
                                {questionsResult.similar_role_in_other_companies.map((q, index) => <li key={index}>{q}</li>)}
                            </ul>

                            <div className="question-category">Behavioral Questions</div>
                            <ul>
                                {questionsResult.behavioral_questions.map((q, index) => <li key={index}>{q}</li>)}
                            </ul>

                            <div className="question-category">Coding Questions</div>
                            <ul>
                                {questionsResult.coding_questions.map((q, index) => <li key={index}>{q}</li>)}
                            </ul>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
}

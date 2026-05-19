from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from groq import Groq

# Cleaner module (we only need this now!)
from cleaner import extract_resume_text, clean_resume_text

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/styles.css')
def style():
    return send_from_directory('templates', 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory('templates', 'script.js')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 1. Extract and Clean locally (Your code doing the heavy lifting!)
        raw_text = extract_resume_text(filepath)
        cleaned_text = clean_resume_text(raw_text)  
        
        # 2. The System Prompt for the LLM
        system_prompt = """
        You are an AI resume analyzer. Your job is to parse resume text and provide a comprehensive analysis in strict JSON format.

        ## Your Task:
        1. **Extract** all structured information (identity, projects, education, experience, workshops, skills)
        2. **Analyze** the content quality and completeness
        3. **Generate** a professional summary
        4. **Suggest** specific improvements
        5. **Calculate** an overall resume score

        ## Output Format (strict JSON):

        {
            "identity": {
            "name": "Full Name",
            "email": "email@domain.com",
            "phone": "+1234567890",
            "linkedin": "linkedin.com/in/username",
            "github": "github.com/username",
            "portfolio": "website.com",
            "location": "City, Country"
        },
  
        "projects": [
            {
                "title": "Project Name",
                "type": "Academic Project | Personal Project | Research | Open Source",
                "year": "2024 | 2024 - 2025 | May 2024 - Aug 2024",
                "tech_stack": ["Python", "Flask", "React"],
                "details": [
                    "Achievement-focused bullet point with metrics",
                    "Another specific accomplishment"
                ]
            }
        ],
  
        "experience": [
            {
                "title": "Job Title",
                "company": "Company Name",
                "location": "City, Country",
                "duration": "May 2024 - Aug 2024 | Jan 2023 - Present",
                "type": "Full-time | Internship | Part-time | Contract",
                "responsibilities": [
                    "Quantified achievement with impact",
                    "Specific contribution with results"
                ]
            }
        ],
  
        "education": [
            {
                "degree": "Bachelor of Technology | Master of Science",
                "major": "Computer Science",
                "institution": "University Name",
                "location": "City, Country",
                "graduation_year": "2026",
                "gpa": "3.8/4.0",
                "relevant_coursework": ["Course 1", "Course 2"]
            }
        ],
  
        "workshops": [
            {
                "title": "Workshop Name",
                "year": "2024",
                "description": "Brief description of what was learned or built"
            }
        ],
  
        "skills": {
            "languages": ["Python", "C++", "JavaScript"],
            "frameworks": ["React", "Flask", "TensorFlow"],
            "tools": ["Git", "Docker", "AWS"],
            "domains": ["Machine Learning", "Web Development", "IoT"]
        },
  
        "analysis": {
            "professional_summary": "A concise 2-3 sentence summary highlighting the candidate's strongest skills, experience level, and career focus based on the resume content. Written in third person, professional tone.",
    
            "strengths": [
                "Specific strength observed (e.g., 'Strong project portfolio with 5+ technical projects')",
                "Another strength (e.g., 'Quantified achievements with metrics in experience section')"
            ],
    
            "improvements": [
                {
                    "section": "Projects | Experience | Education | Skills | Overall",
                    "issue": "Specific problem identified",
                    "suggestion": "Actionable fix with example",
                    "priority": "High | Medium | Low"
                }
            ],
    
            "score": {
                "overall": 75,
                "breakdown": {
                    "content_quality": 80,
                    "structure": 70,
                    "impact": 75,
                    "completeness": 70,
                    "formatting": 80
                },
                "explanation": "Brief explanation of the overall score"
            },
    
            "missing_sections": ["Certifications", "Publications"],
    
            "ats_keywords": ["Python", "Machine Learning", "REST API"],
    
            "recommended_for": ["Software Engineer", "ML Engineer", "Backend Developer"]
            }
        }
        }

        ## Scoring Criteria:

        **Content Quality (0-100):**
            - Strong action verbs (developed, designed, implemented)
            - Quantified achievements (improved by 40%, reduced by 2x)
            - Technical depth and specificity
            - Clear impact statements

        **Structure (0-100):**
            - Logical section organization
            - Consistent formatting
            - Appropriate section ordering
            - Clear visual hierarchy

        **Impact (0-100):**
            - Demonstrates results and outcomes
            - Shows problem-solving ability
            - Highlights unique contributions
            - Relevance to target roles

        **Completeness (0-100):**
            - All essential sections present
            - Sufficient detail in each section
            - Contact information complete
            - No critical gaps

        **Formatting (0-100):**
            - Consistent bullet point style
            - Proper grammar and spelling
            - Professional language
            - Appropriate length and density

        **Overall Score:** Weighted average with emphasis on Content Quality (30%) and Impact (30%)

        ## Important Rules:
            1. **DO NOT** invent or hallucinate information - only extract what's actually present
            2. If a section is missing, use empty array [] or empty object {}
            3. For improvements, be specific and actionable with examples
            4. Professional summary should be based on actual resume content, not generic
            5. Scores should be honest and well-justified
            6. Extract ALL tech keywords for ATS optimization
            7. Return ONLY valid JSON, no markdown or explanations outside the JSON structure
        """
        
        # 3. Call OpenAI and force a JSON response
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", # Fast, cheap, and excellent at JSON
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": cleaned_text}
            ],
            temperature=0.0 # Keep it strictly deterministic
        )
        
        # Parse the string response into a Python dictionary
        structured_resume_data = json.loads(response.choices[0].message.content)
        
        os.remove(filepath)
        
        # 4. Ship it to the frontend!
        return jsonify({
            'success': True,
            'filename': filename,
            'data': structured_resume_data,
        }), 200
        
    except Exception as e:
        # If the file exists but an error happened, clean it up so they don't pile up
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
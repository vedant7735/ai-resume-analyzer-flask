# LLM Analysis Service
# This service will manage OpenAI/Groq client API calls for analyzing resume text.
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ANALYSIS_PROMPT = """
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
      "Specific strength observed",
      "Another strength with examples"
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

## Scoring Criteria:

**Content Quality (0-100):** Strong action verbs, quantified achievements, technical depth
**Structure (0-100):** Logical organization, consistent formatting
**Impact (0-100):** Demonstrates results and problem-solving
**Completeness (0-100):** All essential sections present
**Formatting (0-100):** Professional language and grammar

**Overall Score:** Weighted average with emphasis on Content Quality (30%) and Impact (30%)

## Important Rules:
1. DO NOT invent information - only extract what's present
2. If section missing, use empty array [] or object {}
3. Be specific and actionable in improvements
4. Return ONLY valid JSON
"""


def analyze_resume(cleaned_text):
    """
    Analyze resume using Groq LLM.
    Returns structured JSON data.
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ANALYSIS_PROMPT},
                {"role": "user", "content": cleaned_text}
            ],
            temperature=0.0
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        raise Exception(f"LLM analysis failed: {str(e)}")
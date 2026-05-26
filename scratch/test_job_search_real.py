import sys
import os
import json

# Add the project directory to sys.path
sys.path.append(os.path.abspath('c:/Intern/Project/ai-resume-analyzer-flask'))

from backend.services.jobs.job_search_service import search_live_jobs
import backend.services.caching.cache_service as cache_service

def test_search():
    # Load analysis data
    analysis_file = 'backend/cache/v2_ce0a7e2cd29a13597bb846f6bd7995763f4d87a7be8b4c8118887d1316f8cbaf_866a207c.json'
    if not os.path.exists(analysis_file):
        print(f"Error: {analysis_file} not found.")
        return
        
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
        
    filters = {
        "locations": ["India"],
        "workModes": [],
        "salaryMin": "9",
        "salaryMax": ""
    }
    
    print("Running search_live_jobs...")
    jobs = search_live_jobs(analysis_data, filters)
    
    print(f"Result count: {len(jobs)}")
    for i, j in enumerate(jobs):
        print(f"[{i+1}] Title: {j.get('title')}, Company: {j.get('company')}, Match Score: {j.get('match_score')}")
        print(f"    URL: {j.get('url')}")
        print(f"    Salary: {j.get('salary')}, Min: {j.get('salary_min')}, Max: {j.get('salary_max')}, Currency: {j.get('salary_currency')}")
        print(f"    Reasons: {j.get('match_reasons')}")
        
if __name__ == '__main__':
    test_search()

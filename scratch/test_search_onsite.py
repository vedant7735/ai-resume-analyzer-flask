import sys
import os
import json

# Add the project directory to sys.path
sys.path.append(os.path.abspath('c:/Intern/Project/ai-resume-analyzer-flask'))

from backend.services.jobs.job_search_service import search_live_jobs

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
        "workModes": ["Onsite"],
        "salaryMin": "",
        "salaryMax": ""
    }
    
    print("Running search_live_jobs with India and Onsite...")
    # Clear cache or bypass cache to see live results
    import shutil
    # Just temporarily mock cache check or check cached/uncached
    jobs = search_live_jobs(analysis_data, filters)
    
    print(f"Result count: {len(jobs)}")
    for i, j in enumerate(jobs):
        print(f"[{i+1}] Title: {j.get('title')}")
        print(f"    Company: {j.get('company')}")
        print(f"    Location: {j.get('location')}")
        print(f"    Remote: {j.get('remote')} (type: {type(j.get('remote'))})")
        print(f"    URL: {j.get('url')}")
        print(f"    Match Score: {j.get('match_score')}")
        print(f"    Reasons: {j.get('match_reasons')}")
        print("-" * 50)
        
if __name__ == '__main__':
    test_search()

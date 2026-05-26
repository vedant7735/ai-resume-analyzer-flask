import requests
import json
import os

def test_api():
    analysis_file = 'backend/cache/v2_ce0a7e2cd29a13597bb846f6bd7995763f4d87a7be8b4c8118887d1316f8cbaf_866a207c.json'
    if not os.path.exists(analysis_file):
        print("Analysis file not found")
        return
        
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    payload = {
        "analysis_data": data,
        "filters": {
            "locations": [],
            "workModes": [],
            "salaryMin": "",
            "salaryMax": ""
        }
    }
    
    print("Sending POST request to http://127.0.0.1:5000/find-jobs...")
    try:
        r = requests.post("http://127.0.0.1:5000/find-jobs", json=payload, timeout=30)
        print(f"Status Code: {r.status_code}")
        response_data = r.json()
        print(f"Success: {response_data.get('success')}")
        jobs = response_data.get('jobs', [])
        print(f"Returned {len(jobs)} jobs")
        if jobs:
            print("First job title:", jobs[0].get('title'))
    except Exception as e:
        print(f"Error during request: {e}")

if __name__ == '__main__':
    test_api()

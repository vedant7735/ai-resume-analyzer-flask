"""
End-to-end test: POST to running Flask /find-jobs
Validates the new response shape (jobs, relaxed_filters, applied_filters).
"""
import requests
import json
import os

FLASK_URL = "http://127.0.0.1:5000/find-jobs"

# Load a cached analysis to use as the test profile
ANALYSIS_FILE = "backend/cache/v2_ce0a7e2cd29a13597bb846f6bd7995763f4d87a7be8b4c8118887d1316f8cbaf_866a207c.json"

def run_test(label, filters, expect_relaxed=None):
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"Filters: {filters}")
    print('='*60)

    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)

    payload = {"analysis_data": analysis_data, "filters": filters}
    try:
        resp = requests.post(FLASK_URL, json=payload, timeout=60)
        data = resp.json()
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    print(f"  Status: {resp.status_code}")
    print(f"  success: {data.get('success')}")
    print(f"  relaxed_filters: {data.get('relaxed_filters')}")
    print(f"  applied_filters: {data.get('applied_filters')}")
    jobs = data.get('jobs', [])
    print(f"  Job count: {len(jobs)}")

    if expect_relaxed is not None:
        passed = data.get('relaxed_filters') == expect_relaxed
        print(f"  relaxed_filters == {expect_relaxed}: {'PASS ✓' if passed else 'FAIL ✗'}")

    for i, j in enumerate(jobs[:3]):
        print(f"  [{i+1}] {j.get('title')} @ {j.get('company')} | {j.get('location')} | remote={j.get('remote')} | score={j.get('match_score')}")

if __name__ == '__main__':
    if not os.path.exists(ANALYSIS_FILE):
        print(f"ERROR: {ANALYSIS_FILE} not found. Upload a resume first.")
        exit(1)

    # Test 1: India + Onsite → should trigger relaxed fallback since all fallback APIs are remote
    run_test(
        "India + Onsite (expect relaxed=True if DDG fails)",
        {"locations": ["India"], "workModes": ["Onsite"], "salaryMin": "", "salaryMax": ""},
    )

    # Test 2: No filters → should work without relaxation
    run_test(
        "No filters (expect relaxed=False)",
        {"locations": [], "workModes": [], "salaryMin": "", "salaryMax": ""},
        expect_relaxed=False,
    )

    # Test 3: Remote only → should work without relaxation
    run_test(
        "Remote only (expect relaxed=False)",
        {"locations": [], "workModes": ["Remote"], "salaryMin": "", "salaryMax": ""},
        expect_relaxed=False,
    )

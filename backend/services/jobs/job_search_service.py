import os
import json
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
import json_repair
import backend.services.caching.cache_service as cache_service
from backend.services.model_service.config.model_registry import MODEL_REGISTRY_JOB_SEARCH
from duckduckgo_search import DDGS

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

JOB_SEARCH_PROMPT = """
You are a specialized job search AI with web search capabilities.

Your ONLY task is to find REAL, CURRENTLY ACTIVE job postings that match the candidate profile below.
Search globally / everywhere. Do NOT restrict results to any single country unless the candidate profile specifies a preferred location.

============================================================
PRIORITY SYSTEM — follow this strictly:
  P1 (NON-NEGOTIABLE): Seniority level and key skills from the MANDATORY REQUIREMENTS section.
                       Every single result MUST match these. Reject any posting that does not.
  P2 (STRONG PREFERENCE): Target role / job title family.
                           Prioritise exact title matches; near-matches are acceptable.
  P3 (OPTIONAL / NICE-TO-HAVE): Location, work mode, salary range from the PREFERENCES section.
                                 Use these to rank results, NOT to exclude them.
If honouring a P3 preference would force you to return a P1-violating result, ignore the P3 preference instead.
============================================================

STRICT RULES:
1. You MUST use web_search to find jobs — DO NOT invent or hallucinate listings
2. Search LinkedIn, Wellfound, Indeed, Glassdoor, Naukri, Instahiring, or direct company career pages
3. Only include jobs posted within the LAST 14 DAYS
4. Return AT LEAST 20 UNIQUE jobs from 20 DIFFERENT companies
5. Every job MUST have a working, direct application URL (not a search results page)

SALARY RULES:
- Copy the EXACT salary string as written on the posting (e.g. "₹15,00,000", "12L-18L", "$120k", "£60,000", "€80,000", "A$90k")
- If NO salary is visible, set salary to null
- NEVER estimate or fabricate a salary figure

URL REQUIREMENTS:
- Must be a DIRECT link to the specific job posting, not a search results or generic careers page
- Format: https://company.com/careers/job/[job-id]  OR  https://linkedin.com/jobs/view/[id]

SEARCH STRATEGY — execute in order:
  Step 1 → Read the MANDATORY REQUIREMENTS section in the candidate profile below.
            Lock in the exact seniority level and top skills — these drive every search query.
  Step 2 → Build queries: "[seniority_level] [role] [key_skill_1] [key_skill_2] jobs"
            Run queries on multiple boards. Do NOT add a country to the query unless PREFERRED LOCATIONS are listed.
  Step 3 → Filter results: keep only postings ≤14 days old that match the P1 seniority and skills.
  Step 4 → If PREFERRED LOCATIONS are listed, apply them as a secondary filter to rank results higher — not to exclude.
  Step 5 → Extract EXACT details from each posting (title, company, location, salary, URL) — do not paraphrase.
  Step 6 → Verify the application URL is specific and reachable.

---

CANDIDATE PROFILE:
{context}

---

OUTPUT FORMAT — return ONLY a valid JSON object, no markdown, no explanation, no code fences:

{{
  "jobs": [
    {{
      "title": "exact job title from posting",
      "company": "exact company name",
      "location": "City, Country  OR  Remote",
      "remote": true or false,
      "salary": "exactly as written on site" or null,
      "posted_days_ago": integer,
      "url": "https://direct-application-link.com/job/123",
      "requirements": ["skill1", "skill2", "skill3"]
    }}
  ]
}}

VALIDATION CHECKLIST — verify every item before returning:
☐ Every job matches the P1 seniority level (no senior roles for junior candidates, and vice versa)
☐ Every job requires at least one of the candidate's key skills
☐ At least 20 jobs from 20 different companies
☐ Every URL is a direct application link (not search results)
☐ Salaries are exactly as written or null — no invented figures
☐ All jobs posted within last 14 days
☐ JSON is valid (no trailing commas, proper quotes)

Return the JSON now.
"""

def generate_search_query_context(analysis_data, filters=None):
    """
    Build a FOCUSED, STRUCTURED context for job search that respects UI filters.
    """
    filters = filters or {}
    jd_match = analysis_data.get("jd_match", {})
    analysis = analysis_data.get("analysis", {})
    identity = analysis_data.get("identity", {})
    skills = analysis_data.get("skills", {})
    experience = analysis_data.get("experience", [])
    
    # === TARGET ROLE ===
    if jd_match and jd_match.get("role_title"):
        target_role = jd_match["role_title"]
    elif analysis.get("recommended_for"):
        target_role = analysis["recommended_for"][0]
    else:
        target_role = "Software Engineer"
    
    # === SKILLS (ranked by importance) ===
    primary_skills = skills.get("languages", [])[:3]
    secondary_skills = skills.get("frameworks", [])[:3]
    tools = skills.get("tools", [])[:3]
    
    all_skills = primary_skills + secondary_skills + tools
    skills_str = ", ".join(all_skills[:8])  # Limit to top 8
    
    # === EXPERIENCE LEVEL ===
    years_experience = len(experience)
    if years_experience == 0:
        exp_level = "Entry Level / Fresher (0-1 years)"
    elif years_experience == 1:
        exp_level = "Junior (1-2 years)"
    elif years_experience == 2:
        exp_level = "Mid-Level (2-4 years)"
    else:
        exp_level = f"Senior / Lead ({years_experience-1}-{years_experience+1} years)"
    
    # === JD-SPECIFIC KEYWORDS (if available) ===
    jd_keywords = ""
    if jd_match and jd_match.get("matched_keywords"):
        matched = jd_match["matched_keywords"][:5]
        jd_keywords = f"\nJob Description Keywords: {', '.join(matched)}"
    
    context = f"""
=== CRITICAL MANDATORY REQUIREMENTS (MUST MATCH EXACTLY - NOT PREFERENCES) ===
TARGET ROLE: {target_role}
EXPERIENCE/SENIORITY LEVEL: {exp_level}
KEY SKILLS: {skills_str}{jd_keywords}

SKILL BREAKDOWN:
    - Primary: {', '.join(primary_skills) if primary_skills else 'None listed'}
    - Frameworks: {', '.join(secondary_skills) if secondary_skills else 'None listed'}
    - Tools: {', '.join(tools) if tools else 'None listed'}

DIRECTIVE: You are looking for jobs specifically matching this skillset and seniority level. These are absolute requirements and CANNOT be treated as preferences.

=== CANDIDATE PREFERENCES (STRICTLY OPTIONAL) ===
These are secondary preferences. Try to find jobs matching these where possible, but prioritize the skill match and seniority level above everything else. Do NOT restrict the search geographically if it prevents finding jobs matching the skillset and seniority.
"""
    
    # Candidate's current location from resume
    cand_loc = identity.get("location", "").strip()
    if cand_loc:
        context += f"CANDIDATE CURRENT LOCATION: {cand_loc}\n"
    
    # Preferred Locations from filters
    if filters.get('locations') and len(filters['locations']) > 0:
        context += f"PREFERRED JOB LOCATIONS: {', '.join(filters['locations'])}\n"
        
    # Preferred Work Modes from filters
    if filters.get('workModes') and len(filters['workModes']) > 0:
        context += f"PREFERRED WORK MODES: {', '.join(filters['workModes'])}\n"
        
    # Preferred Salary from filters
    salary_min = filters.get('salaryMin')
    salary_max = filters.get('salaryMax')
    if salary_min or salary_max:
        salary_str_parts = []
        if salary_min:
            salary_str_parts.append(f"Min: {salary_min} LPA")
        if salary_max:
            salary_str_parts.append(f"Max: {salary_max} LPA")
        context += f"PREFERRED SALARY RANGE: {' - '.join(salary_str_parts)}\n"
        
    return context.strip()

import re
def is_valid_url(url: str) -> bool:
    """Check if URL is valid and not a completely generic non-job page.
    
    We used to block all /search and /jobs paths, but Indian job boards like
    Naukri, Indeed IN, Internshala etc. use those patterns for real listings.
    Only block homepage-level paths and known search-result-aggregator pages
    that don't link to a specific posting.
    """
    if not url or len(url) < 10:
        return False
    if not url.startswith(("http://", "https://")):
        return False
    if url.count('/') < 3:
        return False
        
    # Block ONLY truly generic patterns — bare domain homepages and LinkedIn/Google job searches
    blocked_patterns = [
        r"^https?://[^/]+/?$",                 # bare domain homepage
        r"linkedin\.com/jobs/search",           # LinkedIn search results
        r"google\.com/search",                  # Google search
        r"bing\.com/search",                    # Bing search
        r"duckduckgo\.com/\?",                  # DDG search
    ]
    for pattern in blocked_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    return True

# Approximate annual exchange rates to INR (update periodically)
_CURRENCY_TO_INR = {
    'usd': 90.0,
    'gbp': 120.0,
    'eur': 105.0,
    'aud': 60.0,
    'cad': 68.0,
    'sgd': 72.0,
    'aed': 25.0,
    'inr': 1.0,
}

def _detect_currency(s: str) -> tuple[str, float]:
    """Return (currency_code, inr_per_unit) for the salary string."""
    if '£' in s or 'gbp' in s:
        return 'GBP', _CURRENCY_TO_INR['gbp']
    if '€' in s or 'eur' in s:
        return 'EUR', _CURRENCY_TO_INR['eur']
    # CAD must come before AUD — 'ca$' contains 'a$'
    if 'ca$' in s or 'cad' in s or 'c$' in s:
        return 'CAD', _CURRENCY_TO_INR['cad']
    if 'a$' in s or 'aud' in s:
        return 'AUD', _CURRENCY_TO_INR['aud']
    if 'sgd' in s or 's$' in s:
        return 'SGD', _CURRENCY_TO_INR['sgd']
    if 'aed' in s or 'د.إ' in s:
        return 'AED', _CURRENCY_TO_INR['aed']
    if '$' in s or 'usd' in s:
        return 'USD', _CURRENCY_TO_INR['usd']
    if '₹' in s or 'inr' in s or 'lpa' in s or 'lakh' in s or 'lac' in s:
        return 'INR', _CURRENCY_TO_INR['inr']
    # Default — assume INR for bare numbers
    return 'INR', _CURRENCY_TO_INR['inr']

def extract_salary_bounds(salary_str):
    """Parse a raw salary string into (min_lpa, max_lpa, currency_code).

    Returns (None, None, None) if the salary cannot be parsed.
    All values are normalised to approximate annual LPA (Lakhs Per Annum)
    for internal comparison, regardless of source currency.
    """
    if not salary_str:
        return None, None, None

    s = str(salary_str).lower().replace(',', '')
    currency, inr_rate = _detect_currency(s)

    is_monthly = any(w in s for w in ['/mo', '/ month', 'per month', 'monthly', ' p.m.', 'pm', '/month'])
    is_hourly  = any(w in s for w in ['/hr', '/ hour', 'per hour', 'hourly', 'an hour', '/hour'])
    is_lpa_unit = currency == 'INR' and any(w in s for w in ['lpa', 'lakh', 'lac', ' l ', 'l per'])

    numbers = []
    matches = re.findall(r'(\d+(?:\.\d+)?)', s)

    for m in matches:
        val = float(m)

        # Expand shorthand suffixes BEFORE currency conversion
        if 'k' in s and val < 10000:
            val = val * 1000                     # e.g. $120k → 120000
        elif is_lpa_unit and val < 1000:
            val = val * 100000                   # e.g. 12 LPA → 1200000 INR
        elif currency == 'INR' and val >= 100000:
            pass                                 # already in absolute INR
        elif currency == 'INR' and val < 1000 and not is_lpa_unit:
            val = val * 100000                   # bare "12" for INR → treat as lakhs

        # Annualise if needed
        if is_hourly:
            val = val * 2080                     # ~40 hrs/week × 52 weeks
        elif is_monthly:
            val = val * 12

        # Convert to INR (absolute annual)
        val_inr = val * inr_rate if currency != 'INR' else val

        # Convert to LPA
        lpa = val_inr / 100000
        numbers.append(lpa)

    if not numbers:
        return None, None, None

    numbers.sort()

    # Filter out noise (years like 2024, day counts like 30, etc.)
    valid_nums = [n for n in numbers if 0.5 <= n <= 5000]

    if not valid_nums:
        return None, None, None

    return valid_nums[0], valid_nums[-1], currency

def deduplicate_jobs(jobs):
    seen = set()
    unique_jobs = []
    for job in jobs:
        title = str(job.get('title') or '').lower().strip()
        company = str(job.get('company') or '').lower().strip()
        location = str(job.get('location') or '').lower().strip()
        key = f"{title}|{company}|{location}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    return unique_jobs

def calculate_job_match(job, analysis_data, filters=None):
    filters = filters or {}
    score = 0
    reasons = []
    
    # 1. Skill overlap (40%)
    skills_dict = analysis_data.get('skills', {})
    resume_skills_raw = []
    if isinstance(skills_dict, dict):
        for val in skills_dict.values():
            if isinstance(val, list):
                resume_skills_raw.extend(val)
            elif isinstance(val, str):
                resume_skills_raw.append(val)
    elif isinstance(skills_dict, list):
        resume_skills_raw = skills_dict

    resume_skills = {str(s).lower().strip() for s in resume_skills_raw}
    job_reqs_raw = job.get('requirements', [])
    job_reqs = {str(r).lower().strip() for r in job_reqs_raw}
    
    if job_reqs:
        overlap = resume_skills.intersection(job_reqs)
        skill_score = (len(overlap) / len(job_reqs)) * 40
        score += skill_score
        
        display_overlap = [r for r in job_reqs_raw if str(r).lower().strip() in overlap]
        if display_overlap:
            reasons.append(f"Matches {len(display_overlap)} skills ({', '.join(display_overlap[:3])})")
    else:
        score += 20
        
    # 2. Role similarity (20%)
    job_title = str(job.get('title') or '').lower()
    experience = analysis_data.get('experience', [])
    current_role = experience[0].get('title', '').lower() if experience else "software engineer"
    
    if current_role in job_title or any(word in job_title for word in current_role.split()):
        score += 20
        reasons.append("Strong role match")
    else:
        score += 10
        
    # 3. Experience overlap (15%)
    is_senior = 'senior' in job_title or 'lead' in job_title or 'staff' in job_title or 'principal' in job_title
    is_candidate_senior = 'senior' in current_role or 'lead' in current_role or len(experience) >= 3
    if is_senior == is_candidate_senior:
        score += 15
    else:
        score += 5
        
    # 4. User Priority Filters (Bonus points up to +40)
    
    # Check Location Preference
    pref_locs = filters.get('locations', [])
    job_loc = str(job.get('location') or '').lower()
    if pref_locs and any(ploc.lower() in job_loc for ploc in pref_locs):
        score += 15
        reasons.append(f"Preferred Location: {pref_locs[0]}")
        
    # Check Work Mode Preference
    pref_modes = filters.get('workModes', [])
    is_remote = job.get('remote', False)
    if pref_modes:
        if ('Remote' in pref_modes and is_remote) or ('Onsite' in pref_modes and not is_remote) or ('Hybrid' in pref_modes):
            score += 15
            reasons.append("Preferred Work Mode")
            
    # Check Salary Preference
    s_min_filter = filters.get('salaryMin')
    s_max_filter = filters.get('salaryMax')
    j_min, j_max, j_currency = extract_salary_bounds(job.get('salary'))

    # Store for UI (LPA equivalents + detected currency)
    if j_min is not None:
        job['salary_min'] = j_min
    if j_max is not None:
        job['salary_max'] = j_max
    if j_currency is not None:
        job['salary_currency'] = j_currency

    if (s_min_filter or s_max_filter) and (j_min is not None or j_max is not None):
        try:
            s_min_val = float(s_min_filter) if s_min_filter else 0
            s_max_val = float(s_max_filter) if s_max_filter else 9999

            # Job salary range overlaps with user's preferred LPA range
            if j_max >= s_min_val and j_min <= s_max_val:
                score += 25
                reasons.append("Salary in preferred range")
        except (ValueError, TypeError):
            pass
        
    job['match_score'] = min(round(score), 100)
    job['match_reasons'] = reasons
    return job

def fetch_api_jobs_fallback(target_role, key_skills):
    import requests
    print(f"[JOB SEARCH] Executing public API fallback for role: '{target_role}', skills: {key_skills}")
    jobs = []
    
    # 1. RemoteOK
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get('https://remoteok.com/api', headers=headers, timeout=5)
        if r.status_code == 200:
            rok_jobs = r.json()
            for item in rok_jobs[1:]:
                title = item.get('position', '')
                company = item.get('company', '')
                description = item.get('description', '')
                tags = item.get('tags', [])
                
                title_lower = title.lower()
                role_words = [w.lower() for w in target_role.split() if len(w) > 2]
                
                # Check if title contains any keyword from the target role
                if not role_words or any(w in title_lower for w in role_words):
                    matching_skills = [s for s in key_skills if s.lower() in title_lower or s.lower() in [t.lower() for t in tags] or s.lower() in description.lower()]
                    
                    salary_str = None
                    if item.get('salary_min') or item.get('salary_max'):
                        salary_str = f"${item.get('salary_min')} - ${item.get('salary_max')}"
                        
                    jobs.append({
                        "title": title,
                        "company": company or "Unknown",
                        "location": item.get('location') or "Remote",
                        "remote": True,
                        "salary": salary_str,
                        "posted_days_ago": 1,
                        "url": item.get('url'),
                        "requirements": matching_skills[:5]
                    })
    except Exception as e:
        print(f"[JOB SEARCH] RemoteOK fallback failed: {e}")
        
    # 2. Arbeitnow
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get('https://arbeitnow.com/api/job-board-api', headers=headers, timeout=5)
        if r.status_code == 200:
            an_jobs = r.json().get('data', [])
            for item in an_jobs:
                title = item.get('title', '')
                company = item.get('company_name', '')
                description = item.get('description', '')
                tags = item.get('tags', [])
                
                title_lower = title.lower()
                role_words = [w.lower() for w in target_role.split() if len(w) > 2]
                
                if not role_words or any(w in title_lower for w in role_words):
                    matching_skills = [s for s in key_skills if s.lower() in title_lower or s.lower() in [t.lower() for t in tags] or s.lower() in description.lower()]
                    
                    jobs.append({
                        "title": title,
                        "company": company or "Unknown",
                        "location": item.get('location') or "Germany",
                        "remote": item.get('remote', False),
                        "salary": None,
                        "posted_days_ago": 2,
                        "url": item.get('url'),
                        "requirements": matching_skills[:5]
                    })
    except Exception as e:
        print(f"[JOB SEARCH] Arbeitnow fallback failed: {e}")
        
    # 3. The Muse
    try:
        muse_url = 'https://www.themuse.com/api/public/jobs'
        params = {
            'category': 'Software Engineering',
            'page': 1
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(muse_url, params=params, headers=headers, timeout=5)
        if r.status_code == 200:
            muse_data = r.json()
            for item in muse_data.get('results', []):
                title = item.get('name', '')
                company = item.get('company', {}).get('name', 'Unknown')
                locations = [loc.get('name') for loc in item.get('locations', [])]
                location_str = locations[0] if locations else "Remote"
                
                title_lower = title.lower()
                role_words = [w.lower() for w in target_role.split() if len(w) > 2]
                
                if not role_words or any(w in title_lower for w in role_words):
                    matching_skills = [s for s in key_skills if s.lower() in title_lower or s.lower() in item.get('contents', '').lower()]
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location_str,
                        "remote": "Remote" in location_str or "Flexible" in location_str,
                        "salary": None,
                        "posted_days_ago": 1,
                        "url": item.get('refs', {}).get('landing_page'),
                        "requirements": matching_skills[:5]
                    })
    except Exception as e:
        print(f"[JOB SEARCH] The Muse fallback failed: {e}")
        
    # 4. Remotive
    try:
        remotive_url = 'https://remotive.com/api/remote-jobs'
        params = {
            'category': 'software-dev',
            'limit': 20
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(remotive_url, params=params, headers=headers, timeout=5)
        if r.status_code == 200:
            for j in r.json().get('jobs', []):
                title = j.get('title', '')
                company = j.get('company_name', 'Unknown')
                location_str = j.get('candidate_required_location') or 'Remote'
                
                title_lower = title.lower()
                role_words = [w.lower() for w in target_role.split() if len(w) > 2]
                
                if not role_words or any(w in title_lower for w in role_words):
                    matching_skills = [s for s in key_skills if s.lower() in title_lower or s.lower() in j.get('description', '').lower()]
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location_str,
                        "remote": True,
                        "salary": j.get('salary') or None,
                        "posted_days_ago": 1,
                        "url": j.get('url'),
                        "requirements": matching_skills[:5]
                    })
    except Exception as e:
        print(f"[JOB SEARCH] Remotive fallback failed: {e}")
        
    # 5. We Work Remotely
    try:
        import xml.etree.ElementTree as ET
        wwr_url = 'https://weworkremotely.com/categories/remote-programming-jobs.rss'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(wwr_url, headers=headers, timeout=5)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            items = root.findall('.//item')
            for item in items[:20]:
                raw_title = item.find('title').text if item.find('title') is not None else ''
                url = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                
                # Split raw title (WWR uses Company: Position format)
                if ':' in raw_title:
                    company, title = raw_title.split(':', 1)
                    company = company.strip()
                    title = title.strip()
                else:
                    company = "Unknown"
                    title = raw_title.strip()
                    
                title_lower = title.lower()
                role_words = [w.lower() for w in target_role.split() if len(w) > 2]
                
                if not role_words or any(w in title_lower for w in role_words):
                    matching_skills = [s for s in key_skills if s.lower() in title_lower or s.lower() in description.lower()]
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "remote": True,
                        "salary": None,
                        "posted_days_ago": 1,
                        "url": url,
                        "requirements": matching_skills[:5]
                    })
    except Exception as e:
        print(f"[JOB SEARCH] We Work Remotely fallback failed: {e}")
        
    return jobs

def search_live_jobs(analysis_data, filters=None):
    filters = filters or {}
    
    # Check cache first
    cached_jobs = cache_service.get_cached_jobs(analysis_data, filters)
    if cached_jobs is not None:
        return cached_jobs

    provider = "openai"
    model_to_use = "gpt-4o-mini"
    try:
        job_search_cfg = MODEL_REGISTRY_JOB_SEARCH.get("job_search", {})
        provider = job_search_cfg.get("provider", provider)
        model_to_use = job_search_cfg.get("model", model_to_use)
    except Exception:
        pass

    if provider == "groq":
        client = groq_client
        use_ddg = True
    else:
        client = openai_client
        use_ddg = False
        
    jobs = []

    if use_ddg:
        # ─── DUCKDUCKGO + GROQ/COMPLETIONS PIPELINE ───────────────────────
        jd_match = analysis_data.get("jd_match", {})
        analysis = analysis_data.get("analysis", {})
        skills = analysis_data.get("skills", {})
        experience = analysis_data.get("experience", [])
        
        if jd_match and jd_match.get("role_title"):
            target_role = jd_match["role_title"]
        elif analysis.get("recommended_for"):
            target_role = analysis["recommended_for"][0]
        else:
            target_role = "Software Engineer"
            
        primary_skills = skills.get("languages", [])[:3]
        secondary_skills = skills.get("frameworks", [])[:3]
        all_skills = primary_skills + secondary_skills
        years_experience = len(experience)
        
        query_parts = []
        if years_experience >= 3:
            query_parts.append("Senior")
        elif years_experience <= 1:
            query_parts.append("Junior")
            
        query_parts.append(target_role)
        
        # Primary skills (only add if not already in role title to keep query clean)
        role_lower = target_role.lower()
        for skill in primary_skills[:2]:
            if skill.lower() not in role_lower:
                query_parts.append(skill)
            
        pref_locs = filters.get('locations', [])
        if pref_locs:
            query_parts.append(pref_locs[0])
        else:
            pref_modes = filters.get('workModes', [])
            if 'Remote' in pref_modes:
                query_parts.append("Remote")
                
        query_parts.append("jobs")
        
        # Clean query by removing duplicate tokens and retaining order
        seen_tokens = set()
        clean_parts = []
        for part in query_parts:
            part_clean_words = []
            for word in part.split():
                w_lower = word.lower()
                if w_lower not in seen_tokens:
                    seen_tokens.add(w_lower)
                    part_clean_words.append(word)
            if part_clean_words:
                clean_parts.append(" ".join(part_clean_words))
                
        query_str = " ".join(clean_parts)
        
        print(f"[JOB SEARCH] Executing DuckDuckGo query: {query_str}")
        
        search_results = []
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query_str, max_results=15))
        except Exception as e:
            print(f"[JOB SEARCH] DuckDuckGo search failed: {e}")
            
        if search_results:
            # Format search results into plain text
            results_text = ""
            for idx, r in enumerate(search_results):
                results_text += f"[{idx}] Title: {r.get('title')}\nURL: {r.get('href')}\nDescription: {r.get('body')}\n\n"
                
            extraction_prompt = f"""You are a specialized job search assistant.
Analyze the following web search results and extract matching active job postings.

CANDIDATE PROFILE:
- Target Role: {target_role}
- Seniority Level: {"Senior" if years_experience >= 3 else "Junior/Mid"}
- Key Skills: {", ".join(all_skills) if all_skills else "Software Engineering"}

SEARCH RESULTS:
============================================================
{results_text}
============================================================

Extract up to 10 matching jobs from the search results.
For each job, extract:
- title: exact job title from posting
- company: company name (look closely at the job title, e.g. "Position at [Company]" or "Position - [Company]". If the employer company name is not explicitly mentioned, extract the host name from the URL, e.g. "LinkedIn", "Naukri", "Glassdoor", "Internshala" etc. Do NOT use "Not specified" or "Unknown" if you can extract a name from the text or URL)
- location: location (e.g. City, Country or Remote)
- remote: true or false
- salary: exact salary string if mentioned (e.g. "$120k", "£60,000", "₹15L"), or null
- posted_days_ago: integer (default to 1 if not specified)
- url: the exact URL from the search result
- requirements: matching skills from the candidate profile

OUTPUT FORMAT — return ONLY a valid JSON object matching this schema:
{{
  "jobs": [
    {{
      "title": "job title",
      "company": "company name",
      "location": "location name",
      "remote": true,
      "salary": "salary string or null",
      "posted_days_ago": 1,
      "url": "URL link",
      "requirements": ["skill1", "skill2"]
    }}
  ]
}}
"""
            try:
                print(f"[JOB SEARCH] Calling completions API using model: {model_to_use}")
                chat_response = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a specialized job search assistant. Output ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": extraction_prompt
                        }
                    ],
                    temperature=0.1
                )
                raw_text = chat_response.choices[0].message.content.strip()
                print(f"[JOB SEARCH] Raw text from LLM: '{raw_text}'")
                
                # Strip code fences
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                    raw_text = raw_text.strip()
                    
                parsed = json_repair.loads(raw_text)
                jobs = parsed.get("jobs", []) if isinstance(parsed, dict) else parsed
                print(f"[JOB SEARCH] Parsed {len(jobs)} jobs from LLM response.")
                
                # Post-parse cleanup: fill null company from URL domain
                for job in jobs:
                    if not job.get("company"):
                        url = job.get("url", "")
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc.lower()
                            # Strip www. and port
                            domain = re.sub(r'^www\.', '', domain).split(':')[0]
                            # Remove TLD suffixes and country codes for readability
                            # e.g. naukri.com -> Naukri, internshala.com -> Internshala
                            site_name = domain.split('.')[0].capitalize()
                            job["company"] = site_name if site_name else "Unknown"
                        except Exception:
                            job["company"] = "Unknown"
            except Exception as e:
                print(f"[JOB SEARCH] LLM completions failed: {e}")
                jobs = []
    else:
        # ─── STANDARD OPENAI RESPONSES PIPELINE ───────────────────────────
        context = generate_search_query_context(analysis_data, filters)
        prompt = JOB_SEARCH_PROMPT.replace("{context}", context)
        
        try:
            response = client.responses.create(
                model=model_to_use,
                input=prompt,
                tools=[{"type": "web_search"}]
            )
            
            raw_output = response.output
            raw_text = ""
            if isinstance(raw_output, list):
                for item in raw_output:
                    if hasattr(item, 'content') and isinstance(item.content, list):
                        for block in item.content:
                            if hasattr(block, 'text'):
                                raw_text += getattr(block, 'text', '')
                    elif isinstance(item, dict) and 'content' in item:
                        for block in item.get('content', []):
                            if isinstance(block, dict) and 'text' in block:
                                raw_text += block.get('text', '')
                                
            if isinstance(raw_text, str) and raw_text.strip():
                parsed = json_repair.loads(raw_text)
                jobs = parsed.get("jobs", []) if isinstance(parsed, dict) else parsed
            elif isinstance(raw_output, dict):
                jobs = raw_output.get("jobs", [])
            else:
                jobs = raw_output if isinstance(raw_output, list) else []
        except Exception as e:
            print(f"[JOB SEARCH] Responses API failed: {e}")
            jobs = []

    # ─── API FALLBACK RESCUE ──────────────────────────────────────────
    if not jobs:
        print("[JOB SEARCH] Web search returned 0 jobs. Invoking public API fallback search...")
        
        jd_match = analysis_data.get("jd_match", {})
        analysis = analysis_data.get("analysis", {})
        skills = analysis_data.get("skills", {})
        
        if jd_match and jd_match.get("role_title"):
            target_role = jd_match["role_title"]
        elif analysis.get("recommended_for"):
            target_role = analysis["recommended_for"][0]
        else:
            target_role = "Software Engineer"
            
        primary_skills = skills.get("languages", [])[:3]
        secondary_skills = skills.get("frameworks", [])[:3]
        all_skills = primary_skills + secondary_skills
        
        jobs = fetch_api_jobs_fallback(target_role, all_skills)

    # ─── POST-PROCESSING & RANKING ────────────────────────────────────
    try:
        # Strip generic URLs
        valid_url_jobs = [j for j in jobs if is_valid_url(j.get('url', ''))]
        unique_jobs = deduplicate_jobs(valid_url_jobs)
        
        # Enforce strict backend experience filtering
        experience = analysis_data.get('experience', [])
        years_experience = len(experience)
        is_candidate_senior = years_experience >= 3 or any(w in exp.get('title', '').lower() for exp in experience for w in ['senior', 'lead', 'staff', 'principal'])
        
        exp_filtered_jobs = []
        for job in unique_jobs:
            title = str(job.get('title') or '').lower()
            is_job_senior = any(w in title for w in ['senior', 'lead', 'staff', 'principal', 'manager', 'architect'])
            is_job_entry = any(w in title for w in ['junior', 'intern', 'trainee', 'fresher'])
            
            # Hard drop if candidate is Junior but job is Senior
            if not is_candidate_senior and is_job_senior:
                continue
            
            # Hard drop if candidate is Senior but job is Entry-Level
            if is_candidate_senior and is_job_entry:
                continue
                
            exp_filtered_jobs.append(job)
            
        unique_jobs = exp_filtered_jobs
        # Keep a snapshot before location/mode filtering so we can fall back
        pre_filter_jobs = list(unique_jobs)
        
        # Enforce location filtering if user specified a location filter
        pref_locs = filters.get('locations', [])
        pref_modes = filters.get('workModes', [])
        
        # Only allow remote jobs to pass location filter if remote is requested/allowed
        allow_remote = (not pref_modes) or ('Remote' in pref_modes)
        
        if pref_locs:
            loc_filtered_jobs = []
            for job in unique_jobs:
                job_loc = str(job.get('location') or '').lower()
                is_remote = job.get('remote', False)
                matches_loc = any(ploc.lower() in job_loc for ploc in pref_locs)
                if matches_loc or (is_remote and allow_remote):
                    loc_filtered_jobs.append(job)
            unique_jobs = loc_filtered_jobs
            
        # Enforce strict work mode filtering if user specified preferred work modes
        if pref_modes:
            mode_filtered_jobs = []
            for job in unique_jobs:
                is_remote = job.get('remote', False)
                matches_mode = False
                if 'Remote' in pref_modes and is_remote:
                    matches_mode = True
                if 'Onsite' in pref_modes and not is_remote:
                    matches_mode = True
                if 'Hybrid' in pref_modes and not is_remote:
                    matches_mode = True
                if matches_mode:
                    mode_filtered_jobs.append(job)
            unique_jobs = mode_filtered_jobs
        
        # ─── GRACEFUL FILTER RELAXATION ──────────────────────────────
        # If strict filtering left us with nothing AND filters were active,
        # fall back to the pre-filter pool so users still see results.
        # We flag the response so the UI can show an explanatory notice.
        relaxed_filters = False
        if len(unique_jobs) == 0 and (pref_locs or pref_modes) and len(pre_filter_jobs) > 0:
            print(f"[JOB SEARCH] Strict filters ({pref_locs}, {pref_modes}) produced 0 results. "
                  f"Relaxing to pre-filter pool ({len(pre_filter_jobs)} jobs).")
            unique_jobs = pre_filter_jobs
            relaxed_filters = True
        
        scored_jobs = [calculate_job_match(job, analysis_data, filters) for job in unique_jobs]
        scored_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        final_jobs = scored_jobs[:10]
        
        # Tag each job with relaxed info if applicable
        if relaxed_filters:
            for job in final_jobs:
                job['_relaxed_filters'] = True
        
        # Build result payload
        result = {
            'jobs': final_jobs,
            'relaxed_filters': relaxed_filters,
            'applied_filters': {
                'locations': pref_locs,
                'workModes': pref_modes
            }
        }
        cache_service.save_jobs_to_cache(analysis_data, filters, result)
        return result
        
    except Exception as e:
        print(f"Job Search Post-processing Error: {str(e)}")
        return {'jobs': [], 'relaxed_filters': False, 'applied_filters': {}}

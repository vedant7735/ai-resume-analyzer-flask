import requests

def test():
    url = 'https://remotive.com/api/remote-jobs'
    params = {
        'category': 'software-dev',
        'limit': 10
    }
    print(f"Requesting {url} with params {params}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            jobs = data.get('jobs', [])
            print(f"Returned {len(jobs)} jobs")
            for idx, j in enumerate(jobs[:5]):
                print(f"[{idx}] {j.get('title')} at {j.get('company_name')} - URL: {j.get('url')}")
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()

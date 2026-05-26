import requests

def test():
    url = 'https://www.themuse.com/api/public/jobs'
    params = {
        'category': 'Software Engineering',
        'location': 'India',
        'page': 1
    }
    print(f"Requesting {url} with params {params}...")
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', [])
            print(f"Returned {len(results)} jobs")
            for idx, item in enumerate(results[:5]):
                company_name = item.get('company', {}).get('name', 'Unknown')
                locations = [loc.get('name') for loc in item.get('locations', [])]
                print(f"[{idx}] {item.get('name')} at {company_name} ({', '.join(locations)}) - URL: {item.get('refs', {}).get('landing_page')}")
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()

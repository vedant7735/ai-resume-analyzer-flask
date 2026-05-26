import requests

def test_query(param_name, val):
    url = 'https://www.themuse.com/api/public/jobs'
    params = {
        'category': 'Software Engineering',
        param_name: val,
        'page': 1
    }
    print(f"Testing {param_name}={val}...")
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            results = r.json().get('results', [])
            print(f"  Returned {len(results)} jobs")
            for idx, item in enumerate(results[:3]):
                company = item.get('company', {}).get('name', 'Unknown')
                locs = [l.get('name') for l in item.get('locations', [])]
                print(f"  [{idx}] {item.get('name')} at {company} ({', '.join(locs)})")
        else:
            print(f"  Failed: {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    test_query('location', 'India')
    test_query('locations', 'India')
    test_query('location', 'Bangalore')
    test_query('location', 'Remote')

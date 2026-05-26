import requests

def test():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = 'https://remoteok.com/api'
    print(f"Requesting {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Returned {len(data)} items")
            for idx, item in enumerate(data[1:]):
                print(f"[{idx}] {item.get('position')}")
        else:
            print("Response content:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()

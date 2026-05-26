import requests
import xml.etree.ElementTree as ET

def test():
    url = 'https://weworkremotely.com/categories/remote-programming-jobs.rss'
    print(f"Requesting {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            # Parse XML
            root = ET.fromstring(r.content)
            items = root.findall('.//item')
            print(f"Returned {len(items)} items")
            for idx, item in enumerate(items[:5]):
                title = item.find('title').text if item.find('title') is not None else 'No Title'
                link = item.find('link').text if item.find('link') is not None else 'No Link'
                print(f"[{idx}] {title} - Link: {link}")
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()

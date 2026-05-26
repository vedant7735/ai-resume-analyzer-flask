from duckduckgo_search import DDGS

def test_backend(backend):
    print(f"Testing backend: '{backend}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("Python developer jobs India", backend=backend, max_results=5))
            print(f"  Success! Returned {len(results)} results")
            for idx, r in enumerate(results):
                print(f"    [{idx}] {r.get('title')} - {r.get('href')}")
    except Exception as e:
        print(f"  Failed: {e}")

if __name__ == '__main__':
    test_backend('api')
    test_backend('html')
    test_backend('lite')

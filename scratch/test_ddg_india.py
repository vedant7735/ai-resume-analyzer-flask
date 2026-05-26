from duckduckgo_search import DDGS
import sys

def test():
    query = "Python jobs India"
    print(f"Searching for: '{query}'")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))
            print(f"Returned {len(results)} results")
            for idx, r in enumerate(results):
                print(f"[{idx}] Title: {r.get('title')}\n    URL: {r.get('href')}\n    Body: {r.get('body')[:150]}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()

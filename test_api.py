"""Test script to verify the API works."""
import requests
import json
import time

# Wait a moment for server to be ready
print("Waiting for server to be ready...")
time.sleep(2)

# Test query
url = "http://127.0.0.1:8001/query"
payload = {
    "query": "how do new hires get benefits?",
    "top_k": 3
}

print(f"\nTesting query: '{payload['query']}'\n")

try:
    response = requests.post(url, json=payload, timeout=10)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✓ Success! Received {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Score: {result['score']:.3f}")
            print(f"   Concepts: {', '.join(result['matched_concepts'])}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
    else:
        print(f"✗ Error: HTTP {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("✗ Could not connect to server. Is it running on port 8001?")
except Exception as e:
    print(f"✗ Error: {e}")

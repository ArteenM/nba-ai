"""
Quick test script for Tank01 API
"""
import requests
import json
import os

# Get API key from environment or paste it here temporarily for testing
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', 'b9dd14bfbdmshcc26a0fb341c1cbp17399djsn783236678b26')

url = "https://tank01-fantasy-stats.p.rapidapi.com/getNBAInjuryList"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "tank01-fantasy-stats.p.rapidapi.com"
}

print("Testing Tank01 NBA Injury API...")
print(f"URL: {url}")
print(f"API Key: {RAPIDAPI_KEY[:10]}..." if RAPIDAPI_KEY != 'PASTE_YOUR_KEY_HERE' else "API Key: NOT SET")
print("-" * 60)

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("-" * 60)
    
    data = response.json()
    print(f"Full Response:\n{json.dumps(data, indent=2)}")
    print("-" * 60)
    
    if data.get('body'):
        injuries = data['body']
        print(f"\n✅ Found {len(injuries)} injuries!")
        
        # Show first 3 as examples
        for i, injury in enumerate(injuries[:3]):
            print(f"\nInjury {i+1}:")
            print(f"  Player: {injury.get('longName', 'N/A')}")
            print(f"  Team: {injury.get('team', 'N/A')}")
            print(f"  Description: {injury.get('description', 'N/A')}")
            print(f"  Date: {injury.get('injDate', 'N/A')}")
    else:
        print("\n❌ No injuries found in response")
        print("Possible reasons:")
        print("  1. Free tier doesn't include injury data")
        print("  2. API subscription not active")
        print("  3. Off-season / no current injuries")
        print("  4. Need to upgrade to paid plan")
        
except requests.exceptions.HTTPError as e:
    print(f"\n❌ HTTP Error: {e}")
    print(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
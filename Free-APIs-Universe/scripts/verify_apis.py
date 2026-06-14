import json
import os
import urllib.request
import urllib.error
from datetime import datetime

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        return response.getcode() == 200
    except Exception:
        return False

def verify_apis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    apis_path = os.path.join(base_dir, 'data', 'apis.json')
    
    with open(apis_path, 'r') as f:
        apis = json.load(f)
        
    changed = False
    
    for api in apis:
        # Check docs URL
        docs_url = api.get('documentation')
        if docs_url:
            print(f"Verifying {api['name']}... ", end="")
            is_valid = check_url(docs_url)
            
            if is_valid:
                api['status'] = 'verified'
                print("✅ 200 OK")
            else:
                api['status'] = 'deprecated'
                print("❌ Failed")
            
            api['lastVerified'] = datetime.utcnow().strftime('%Y-%m-%d')
            changed = True
            
    if changed:
        with open(apis_path, 'w') as f:
            json.dump(apis, f, indent=2)
        print("Updated apis.json with new verification statuses.")

if __name__ == "__main__":
    # For demonstration we won't actually hammer the network during setup
    # Uncomment to enable full verification
    # verify_apis()
    print("Verification script ready.")

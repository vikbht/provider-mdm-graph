import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import time
from app.models import Provider
import time
import sys
from app.models import Provider

API_URL = "http://localhost:8000"

def wait_for_api():
    """Wait for API to be healthy."""
    print("Waiting for API to be ready...")
    for _ in range(30):
        try:
            resp = requests.get(f"{API_URL}/health")
            if resp.status_code == 200:
                print("API is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

    return False

def setup_test_data():
    """Ensure the target provider exists in the DB."""
    from app.config import Neo4jConnection
    from app.engine import ProviderMDMEngine
    from app.models import Provider
    
    print("Seeding test provider 'Robert Smith'...")
    p = Provider(
        npi="1234567890",
        first_name="Robert",
        last_name="Smith",
        email="bob.smith@hospital.org",
        phone="+15551234567",
        license_number="MD12345",
        source_system="test_seed"
    )
    
    with Neo4jConnection() as conn:
        engine = ProviderMDMEngine(conn)
        engine.upsert_provider(p)

def test_matching():
    """Test the matching endpoint."""
    print("\n Testing /match endpoint...")
    
    # Provider data (Same as Stage 3 test)
    # npi="1234567890" corresponds to 'Robert Smith' in our seeded/test data
    provider_data = {
        "npi": "1234587890",
        "first_name": "Robert",
        "last_name": "Smith",
        "email": "bob.smith@hospital.org",
        "phone": "+15551234567",
        "license_number": "MD12345"
    }

    resp = requests.post(f"{API_URL}/match", json=provider_data)
    
    if resp.status_code != 200:
        print(f"FAILED: API returned status {resp.status_code}")
        print(resp.text)
        sys.exit(1)
        
    results = resp.json()
    print(f"Success! API returned {len(results)} matches.")
    
    found_match = False
    for m in results:
        print(f"- Match: NPI={m['provider2_npi']}, Score={m['match_score']}, Action={m['recommended_action']}")
        if m['provider2_npi'] == "1234567890":
            found_match = True
            
    if found_match:
        print("VERIFICATION PASSED: Found expected match.")
    else:
        print("VERIFICATION FAILED: Did not find expected match.")
        sys.exit(1)

if __name__ == "__main__":
    if not wait_for_api():
        print("Timed out waiting for API.")
        sys.exit(1)
        
    setup_test_data()
    test_matching()

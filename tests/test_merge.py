import sys
import os
import time
import requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Provider
from app.config import Neo4jConnection
from app.engine import ProviderMDMEngine

API_URL = "http://localhost:8000"

def setup_merge_data():
    """Seed a Target and a Source provider."""
    print("Seeding Target and Source providers...")
    
    # Target (Golden Candidate)
    target = Provider(
        npi="9999900001",
        first_name="Golden",
        last_name="Doctor",
        email="golden@hospital.org",
        phone="+15559990001",
        license_number="MD_GOLD",
        source_system="gold_source"
    )
    
    # Source (Duplicate to be merged)
    source = Provider(
        npi="9999900002",
        first_name="Duplicate",
        last_name="Doctor",
        email="dup@hospital.org",
        phone="+15559990002",
        license_number="MD_DUP",
        source_system="legacy_source"
    )
    
    with Neo4jConnection() as conn:
        engine = ProviderMDMEngine(conn)
        engine.upsert_provider(target)
        engine.upsert_provider(source)

def test_merge_api():
    """Test the /merge API endpoint."""
    print("\n Testing /merge endpoint...")
    
    payload = {
        "target_npi": "9999900001",
        "source_npis": ["9999900002"]
    }
    
    resp = requests.post(f"{API_URL}/merge", json=payload)
    
    if resp.status_code != 200:
        print(f"FAILED: Merge API returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)
        
    result = resp.json()
    print("API Success! Merge executed.")
    
    # Verify Golden Record Status
    if result['is_golden_record'] is True:
        print("VERIFICATION PASSED: Target is marked as golden record.")
    else:
        print("VERIFICATION FAILED: Target is NOT golden.")
        sys.exit(1)

def verify_graph_state():
    """Verify the state in Neo4j directly."""
    print("\n Verifying Graph State...")
    with Neo4jConnection() as conn:
        # Check Source
        res = conn.execute_query("""
            MATCH (s:Provider {npi: '9999900002'})-[r:MERGED_INTO]->(t:Provider {npi: '9999900001'})
            RETURN s.is_active as active, t.is_golden_record as golden, r
        """)
        
        if not res:
            print("VERIFICATION FAILED: Relationship MERGED_INTO not found.")
            sys.exit(1)
            
        record = res[0]
        if record['active'] is False:
             print("VERIFICATION PASSED: Source is inactive.")
        else:
             print(f"VERIFICATION FAILED: Source active state is {record['active']}")

        if record['golden'] is True:
             print("VERIFICATION PASSED: Target is golden.")
             
        print("Graph verification complete.")

if __name__ == "__main__":
    setup_merge_data()
    test_merge_api()
    verify_graph_state()

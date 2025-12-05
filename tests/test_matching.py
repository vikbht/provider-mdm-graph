"""
Test script for Stage 3: Entity Resolution / Matching.
This script demonstrates how the system identifies duplicates.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Neo4jConnection
from app.engine import ProviderMDMEngine
from app.models import Provider
from datetime import datetime

def main():
    with Neo4jConnection() as conn:
        engine = ProviderMDMEngine(conn)
        
        print("--- Setting up Test Data ---")
        # 1. Create an existing provider in the graph
        existing_npi = "1234567890"
        p1 = Provider(
            npi=existing_npi,
            first_name="Robert",
            last_name="Smith",
            email="robert.smith@hospital.org",
            phone="5551234567",
            license_number="MD12345"
        )
        print(f"Upserting existing provider: Dr. {p1.first_name} {p1.last_name} (NPI: {p1.npi})")
        engine.upsert_provider(p1)

        # 2. Simulate an incoming record that is a "fuzzy" duplicate
        # Same NPI (strong match), but different name variation and email format
        incoming_provider = Provider(
            npi=existing_npi,  # Same NPI
            first_name="Bob",  # Variation of Robert
            last_name="Smith",
            email="bob.smith@hospital.org", # Different email
            phone="+15551234567", # Valid formatted phone
            license_number="MD12345"
        )
        
        print(f"\n--- Executing Stage 3: Matching ---")
        print(f"Incoming Candidate: Dr. {incoming_provider.first_name} {incoming_provider.last_name}")
        
        # Run the matching logic
        matches = engine.match_providers(incoming_provider)
        
        print(f"\n--- Match Results ({len(matches)} found) ---")
        for i, m in enumerate(matches, 1):
            print(f"\nMatch #{i}:")
            print(f"  Target NPI: {m.provider2_npi}")
            print(f"  Score: {m.match_score:.2f} (Threshold: >0.85 is High Confidence)")
            print(f"  Type: {m.match_type}")
            print(f"  Matched Attributes: {', '.join(m.matching_attributes)}")
            print(f"  Recommended Action: {m.recommended_action}")
            
            if m.match_score >= 1.0:
                print("  => Result: EXACT MATCH (Auto-Merge)")
            elif m.match_score >= 0.85:
                print("  => Result: HIGH CONFIDENCE (Auto-Merge)")
            else:
                print("  => Result: REVIEW REQUIRED")

if __name__ == "__main__":
    main()

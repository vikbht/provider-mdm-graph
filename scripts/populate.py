"""
Script to populate the graph with 10,000 provider records.
"""
from typing import List
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.generator import generate_dataset
from app.engine import ProviderMDMEngine
from app.config import Neo4jConnection

BATCH_SIZE = 1000
TOTAL_RECORDS = 10000

def main():
    print(f"Starting population of {TOTAL_RECORDS} provider records...")
    start_time = time.time()
    
    with Neo4jConnection() as conn:
        engine = ProviderMDMEngine(conn)
        # Ensure constraints exist
        print("Bootstrapping graph...")
        engine.bootstrap_graph()

        # Check existing count
        res = conn.execute_query("MATCH (p:Provider) RETURN count(p) as count")
        current_count = res[0]["count"]
        print(f"Current provider count: {current_count}")
        
        needed = TOTAL_RECORDS - current_count
        if needed <= 0:
            print("Graph already seeded with sufficient records. Skipping generation.")
            return

        print(f"Need to generate {needed} records...")
        
        total_inserted = 0
        while total_inserted < needed:
            current_batch_size = min(BATCH_SIZE, needed - total_inserted)
            
            # Generate batch
            print(f"Generating batch of {current_batch_size} providers...")
            providers = generate_dataset(current_batch_size)
            
            # Insert batch
            print(f"Inserting batch ({total_inserted + 1} to {total_inserted + current_batch_size})...")
            engine.batch_upsert_providers(providers)
            
            total_inserted += current_batch_size
            print(f"Progress: {current_count + total_inserted}/{TOTAL_RECORDS}")

    elapsed = time.time() - start_time
    if total_inserted > 0:
        print(f"\nCompleted! Inserted {total_inserted} records in {elapsed:.2f} seconds.")
        print(f"Average rate: {total_inserted/elapsed:.0f} records/sec")
    else:
        print("\nDone.")

if __name__ == "__main__":
    main()

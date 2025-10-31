"""Example usage of ProviderMDMEngine."""
from config import Neo4jConnection
from mdm_engine import ProviderMDMEngine
from models import Provider
from sample_data_generator import generate_provider


def main():
    with Neo4jConnection() as conn:
        engine = ProviderMDMEngine(conn)
        engine.bootstrap_graph()

        # Ingest a sample provider
        provider: Provider = generate_provider()
        print("Upserting provider:", provider.npi)
        engine.upsert_provider(provider)

        # Data quality check
        dq = engine.check_data_quality(provider)
        print("Data quality:", dq.model_dump())

        # Matching demo (self-match just for example)
        matches = engine.match_providers(provider)
        for m in matches[:5]:
            print("Match:", m.model_dump())

        print("Done.")


if __name__ == "__main__":
    main()

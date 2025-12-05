# provider-mdm-graph

Master Data Management solution for healthcare provider data using Neo4j graph database.

## Overview
provider-mdm-graph implements a graph-based MDM for healthcare provider data. It includes data models, data quality rules, fuzzy/exact matching, entity merging to golden records, and a simple ingestion/search API powered by Neo4j.

### Architecture
- Neo4j graph database with labels: Provider, Location, Specialty, Credential, Affiliation
- Constraints and indexes defined in config.py (GRAPH_CONSTRAINTS/GRAPH_INDEXES)
- Python engine (app/engine.py) encapsulating graph ops, matching, merging, and quality checks
- Pydantic models (app/models.py) for validation and typing
- Sample data generator (app/generator.py) using Faker
- Example runner (scripts/demo.py)

Graph relationships (examples):
- (Provider)-[:PRACTICES_AT]->(Location)
- (Provider)-[:HAS_SPECIALTY]->(Specialty)
- (Provider)-[:HAS_CREDENTIAL]->(Credential)
- (Provider)-[:AFFILIATED_WITH]->(Affiliation)

## Getting Started

### Prerequisites
- Python
- uv (package manager)
- Docker (optional, for Neo4j via docker-compose)

### Setup
1. Clone the repo
   git clone https://github.com/vikbht/provider-mdm-graph.git
   cd provider-mdm-graph

2. Install dependencies
   uv sync

3. Configure environment
   cp .env.example .env
   # Edit .env to set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

3. Start the application stack
   docker compose up -d --build
   # - Starts Neo4j
   # - Builds and runs the seeder container which populates 10k records if missing

## Usage
Once the containers are running, the `provider-seeder` service automatically checks if data exists. If less than 10,000 records are present, it will generate and insert them.

You can verify the data in Neo4j Browser (http://localhost:7474 - neo4j/your_password_here):
```cypher
MATCH (n:Provider) RETURN count(n)
```

To run the example matching script manually:
```bash
uv run scripts/demo.py
```

## API Documentation

Key classes and methods:

- app.config.Neo4jConnection
  - connect(), close(), execute_query(query, params)
  - GRAPH_CONSTRAINTS / GRAPH_INDEXES
  - DATA_QUALITY_RULES, MATCHING_CONFIG

- app.models
  - Provider, Location, Specialty, Credential, Affiliation, ProviderComplete
  - MatchResult, DataQualityResult, MergeHistory

- app.engine.ProviderMDMEngine
  - bootstrap_graph() -> None
  - upsert_provider(p: Provider) -> Dict
  - upsert_location(loc: Dict) -> Dict
  - link_provider_location(npi: str, location_id: str, rel: str = "PRACTICES_AT") -> None
  - check_data_quality(p: Provider) -> DataQualityResult
  - match_providers(candidate: Provider) -> List[MatchResult]
  - merge_providers(source_npi: str, target_npi: str) -> None
  - get_provider(npi: str) -> Optional[Dict]
  - search_providers(text: str) -> List[Dict]

### Data Quality
Rules in config.DATA_QUALITY_RULES validate NPI, email, phone, and license formats. check_data_quality returns issues and a quality_score (0..1).

### Matching and Merging
- Hybrid exact/fuzzy scoring using configured weights and thresholds
- Recommended actions: merge or review
- Merging uses APOC refactor.mergeNodes to consolidate duplicates into a golden record

## Sample Data
app/generator.py can generate Providers and related entities for demos/tests.

## Docker Compose
docker-compose.yml deploys Neo4j with APOC enabled and mapped ports (7474, 7687). Update NEO4J_AUTH to a secure password.

## Contributing
PRs and issues are welcome. Please include tests and clear descriptions.

## License
This project is provided as-is without a specific license. Add a LICENSE file if needed.

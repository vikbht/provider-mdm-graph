# EXECUTION_GUIDE.md

Comprehensive execution guide for the Provider MDM Graph Database solution.

## Prerequisites
- OS: macOS, Linux, or Windows 10/11 with WSL2
- Git >= 2.30
- Docker Desktop >= 4.x (includes Docker Engine and Docker Compose)
- Neo4j: either via Docker or local Neo4j Desktop (v5.x)
- Node.js >= 18 LTS and npm >= 9 (if running any helper scripts)
- Python 3.10+ and pip (optional for scripts)
- Make (optional convenience)

Ensure the following ports are available:
- 7474 (Neo4j Browser HTTP)
- 7687 (Neo4j Bolt)

Environment variables (example):
- NEO4J_VERSION=5.20
- NEO4J_AUTH=neo4j/neo4jpassword

## 1. Clone the repository
```
# Using SSH
git clone git@github.com:vikbht/provider-mdm-graph.git

# Or HTTPS
git clone https://github.com/vikbht/provider-mdm-graph.git

cd provider-mdm-graph
```

## 2. Project structure overview
```
provider-mdm-graph/
├─ docker/
│  ├─ neo4j.conf                  # Custom Neo4j configuration (if provided)
│  └─ .env                        # Docker-compose overrides (optional)
├─ cypher/                        # Cypher scripts for schema, constraints, data loads
│  ├─ 00_init_constraints.cypher
│  ├─ 10_schema_indexes.cypher
│  ├─ 20_load_reference_data.cypher
│  ├─ 30_algorithms.cypher
│  └─ utils/                      # helper cypher
├─ data/                          # Place CSV/JSON input files here
├─ scripts/                       # Utility scripts (bash/python/node)
├─ notebooks/                     # Optional Jupyter notebooks
├─ README.md
└─ (this) EXECUTION_GUIDE.md
```

Note: Folder names may differ slightly; use the closest equivalents present in the repo.

## 3. Start Neo4j via Docker
Create or update a docker-compose.yml (if not already present) with the following:

```yaml
version: "3.8"
services:
  neo4j:
    image: neo4j:${NEO4J_VERSION-5.20}
    container_name: provider-mdm-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=${NEO4J_AUTH-neo4j/neo4jpassword}
      - NEO4JLABS_PLUGINS=["apoc","graph-data-science"]
      - NEO4J_apoc_export_file_enabled=true
      - NEO4J_apoc_import_file_enabled=true
      - NEO4J_apoc_import_file_use__neo4j__config=true
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
    volumes:
      - ./data:/data
      - ./import:/import
      - ./logs:/logs
      - ./plugins:/plugins
      - ./docker/neo4j.conf:/var/lib/neo4j/conf/neo4j.conf:ro
```

Start the database:
```
docker compose up -d
# or
docker-compose up -d
```

Check logs:
```
docker logs -f provider-mdm-neo4j
```

Default creds (change NEO4J_AUTH in production): neo4j / neo4jpassword

## 4. Initialize schema and constraints
Run Cypher scripts to set up the graph schema. You can do this via:

- Neo4j Browser (http://localhost:7474)
- cypher-shell (CLI)

Using cypher-shell:
```
# Install if needed (inside container)
docker exec -it provider-mdm-neo4j bash
cypher-shell -u neo4j -p neo4jpassword

# From host if cypher-shell available:
cypher-shell -a bolt://localhost:7687 -u neo4j -p neo4jpassword < cypher/00_init_constraints.cypher
cypher-shell -a bolt://localhost:7687 -u neo4j -p neo4jpassword < cypher/10_schema_indexes.cypher
```

Example constraints/indexes (if files not present, run these examples):
```
// Providers
CREATE CONSTRAINT provider_id IF NOT EXISTS
FOR (p:Provider) REQUIRE p.providerId IS UNIQUE;

// Organizations
CREATE CONSTRAINT org_id IF NOT EXISTS
FOR (o:Organization) REQUIRE o.orgId IS UNIQUE;

// Persons
CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (h:Person) REQUIRE h.personId IS UNIQUE;
```

## 5. Load reference and sample data
If the repo includes CSVs in data/, use APOC to load them. Example:
```
// Load Providers
CALL apoc.load.csv('file:///providers.csv') YIELD map AS row
MERGE (p:Provider {providerId: row.provider_id})
SET p += apoc.map.clean(row, [], ['']),
    p.name = row.name,
    p.npi = row.npi;

// Load Organizations
CALL apoc.load.csv('file:///organizations.csv') YIELD map AS row
MERGE (o:Organization {orgId: row.org_id})
SET o += apoc.map.clean(row, [], ['']),
    o.name = row.name;
```

If scripts exist in cypher/20_load_reference_data.cypher:
```
cypher-shell -u neo4j -p neo4jpassword < cypher/20_load_reference_data.cypher
```

## 6. View data in Neo4j Browser
Open http://localhost:7474 and authenticate. Useful queries:
```
// Counts by label
CALL db.labels() YIELD label
CALL apoc.cypher.run("MATCH (n:" + label + ") RETURN count(n) AS c", {}) YIELD value
RETURN label, value.c AS count ORDER BY count DESC;

// Sample subgraph
MATCH p=(n)-[r]->(m) RETURN p LIMIT 50;

// Inspect Providers by NPI
MATCH (p:Provider {npi: '1234567890'}) RETURN p;
```

## 7. Generate sample data (optional)
Example Cypher to generate synthetic providers, organizations, and relationships:
```
UNWIND range(1, 1000) AS i
MERGE (p:Provider {providerId: toString(i)})
SET p.name = 'Provider ' + toString(i), p.npi = toString(1000000000 + i);

UNWIND range(1, 200) AS j
MERGE (o:Organization {orgId: 'ORG-' + toString(j)})
SET o.name = 'Organization ' + toString(j);

// Random memberships
MATCH (p:Provider), (o:Organization)
WITH p, o WHERE rand() < 0.1
MERGE (p)-[:MEMBER_OF]->(o);
```

## 8. Matching and merging (entity resolution)
Basic example using deterministic keys and fuzzy matching with GDS/Apoc:
```
// Deterministic merge by NPI
CALL apoc.periodic.iterate(
  "MATCH (p:Provider) WHERE p.npi IS NOT NULL RETURN p",
  "WITH p MERGE (u:UniqueProvider {npi: p.npi}) MERGE (p)-[:SAME_AS]->(u)",
  {batchSize: 1000, parallel: true}
);

// Fuzzy similarity on names
CALL gds.nodeSimilarity.stream({
  nodeProjection: 'Provider',
  relationshipProjection: {R: {type: 'MEMBER_OF', orientation: 'UNDIRECTED', properties: {}}},
  similarityCutoff: 0.85
})
YIELD node1, node2, similarity
WITH gds.util.asNode(node1) AS a, gds.util.asNode(node2) AS b, similarity
WHERE a <> b
MERGE (a)-[s:SIMILAR_NAME]->(b)
SET s.score = similarity;
```

Merge candidates example:
```
MATCH (a:Provider)-[s:SIMILAR_NAME]->(b:Provider)
WHERE s.score >= 0.9 AND coalesce(a.npi, '') = coalesce(b.npi, '')
MERGE (a)-[:POTENTIAL_DUPLICATE {score: s.score}]->(b);
```

## 9. Running the application (if app layer included)
If this repository ships an application or API, typical steps:
```
# Configure environment
cp .env.example .env      # if provided
# Edit .env with Neo4j bolt url, user, pass
# Example:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=neo4jpassword

# Install dependencies
npm install    # or: pip install -r requirements.txt

# Run
npm run start  # or: python app.py
```

## 10. Testing
Cypher assertions for sanity checks:
```
// No duplicate UniqueProviders by npi
MATCH (u:UniqueProvider)
WITH u.npi AS n, count(*) AS c
WHERE c > 1
RETURN n, c;

// Every Provider either has npi or name
MATCH (p:Provider)
WHERE coalesce(p.npi, '') = '' AND coalesce(p.name, '') = ''
RETURN count(p) AS missingCoreAttrs;
```

## 11. Troubleshooting
- Port already in use: stop other Neo4j instances or change host ports in compose.
- Authentication errors: ensure NEO4J_AUTH matches your login and that you changed default password.
- APOC/GDS missing: verify NEO4JLABS_PLUGINS and that plugins directory is mounted; restart container.
- Import file not found: place files under ./import and reference with file:///filename.csv
- Memory limits: allocate more memory to Docker; configure dbms.memory.heap.max_size and pagecache in neo4j.conf.
- cypher-shell connection refused: ensure container is running and Bolt port is published.

## 12. Advanced usage examples
Graph projections and community detection:
```
CALL gds.graph.project(
  'providerGraph',
  ['Provider','Organization'],
  {MEMBER_OF: {type: 'MEMBER_OF', orientation: 'UNDIRECTED'}}
);

CALL gds.louvain.stream('providerGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId
ORDER BY communityId, name
LIMIT 50;
```

Pairwise linkage scoring:
```
MATCH (a:Provider), (b:Provider)
WHERE id(a) < id(b)
WITH a, b,
  (CASE WHEN a.npi IS NOT NULL AND a.npi = b.npi THEN 1.0 ELSE 0.0 END) +
  (CASE WHEN apoc.text.jaroWinklerDistance(a.name, b.name) > 0.92 THEN 0.5 ELSE 0.0 END) AS score
WHERE score >= 1.0
MERGE (a)-[:MATCH_CANDIDATE {score: score}]->(b);
```

## 13. Maintenance
Backup database:
```
docker exec -it provider-mdm-neo4j neo4j-admin database dump neo4j --to-path=/data/backups
```

Upgrade Neo4j:
- Stop container, change NEO4J_VERSION, review release notes, start again.

## 14. Additional resources
- Neo4j Docs: https://neo4j.com/docs/
- APOC: https://neo4j.com/docs/apoc/current/
- GDS: https://neo4j.com/docs/graph-data-science/current/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
- Docker Neo4j: https://neo4j.com/developer/docker/

---
If anything in this guide does not match the current repo layout, prefer the repository’s scripts and update paths accordingly.

# Software Engineering Artifacts

## System Architecture & workflows

The following UML diagrams document the structure, data models, and core workflows of the Provider MDM Graph application.

### 1. Class Diagram (Backend Data Models)
This diagram illustrates the Pydantic models defined in `app/models.py` which enforce the schema for API communication and internal logic.

```mermaid
classDiagram
    class Provider {
        +String npi
        +String first_name
        +String last_name
        +String email
        +String phone
        +String license_number
        +Boolean is_active
        +Boolean is_golden_record
        +String master_record_id
    }

    class ProviderComplete {
        +List~Location~ locations
        +List~Specialty~ specialties
        +List~Credential~ credentials
    }

    class Location {
        +String location_id
        +String address
        +String city
        +String state
        +String zip_code
    }

    class Specialty {
        +String specialty_code
        +String specialty_name
        +String taxonomy_code
    }

    class Credential {
        +String credential_id
        +String license_number
        +Date expiration_date
        +String status
    }

    class MatchResult {
        +String provider1_npi
        +String provider2_npi
        +Float match_score
        +String recommended_action
    }

    Provider <|-- ProviderComplete
    ProviderComplete "1" *-- "*" Location
    ProviderComplete "1" *-- "*" Specialty
    ProviderComplete "1" *-- "*" Credential
```

### 2. Graph Data Model (Neo4j Schema)
This entity-relationship diagram shows how data is stored in the Neo4j graph database, highlighting the relationships between entities and the lineage tracking.

```mermaid
erDiagram
    Provider ||--o{ Location : PRACTICES_AT
    Provider ||--o{ Specialty : HAS_SPECIALTY
    Provider ||--o{ Credential : CREDENTIALED_AS
    Provider ||--o{ Affiliation : AFFILIATED_WITH
    Provider ||--o{ Provider : MERGED_INTO

    Provider {
        string npi
        string name
        boolean is_active
        boolean is_golden_record
    }

    Location {
        string address
        string city
        string state
    }

    Specialty {
         string name
         string taxonomy
    }
```

### 3. Sequence Diagram (Merge Workflow)
This diagram details the flow of interactions when a user identifies and merges a duplicate provider record into a Golden Record.

```mermaid
sequenceDiagram
    participant User
    participant Frontend as React UI
    participant API as FastAPI
    participant Engine as MDM Engine
    participant DB as Neo4j Graph

    User->>Frontend: Select "Match & Dedupe"
    User->>Frontend: Input Provider Details
    Frontend->>API: POST /match
    API->>Engine: match_providers(candidate)
    Engine->>DB: Query Potential Matches
    DB-->>Engine: Returns Candidates
    Engine-->>API: MatchResult List (Scored)
    API-->>Frontend: JSON Response
    
    User->>Frontend: Clicks "MERGE" on Duplicate
    Frontend->>API: POST /merge {target, source}
    API->>Engine: merge_providers(target, source)
    
    rect rgb(240, 248, 255)
        note right of Engine: "Link & Flag" Strategy
        Engine->>DB: CREATE (source)-[:MERGED_INTO]->(target)
        Engine->>DB: SET source.is_active = false
        Engine->>DB: SET target.is_golden_record = true
        Engine->>DB: COPY Relationships (Loc, Spec) to Target
    end
    
    Engine-->>API: Updated Target Provider
    API-->>Frontend: Success Response
    Frontend-->>User: Show "Merge Successful" Banner
```

"""Configuration module for MDM system."""
import os
from typing import Dict, List
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnection:
    """Manages Neo4j database connections."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            print(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            print("Connection closed")
    
    def execute_query(self, query: str, parameters: Dict = None):
        """Execute a Cypher query."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Data Quality Rules Configuration
DATA_QUALITY_RULES = {
    'npi': {
        'required': True,
        'pattern': r'^\d{10}$',
        'description': 'NPI must be exactly 10 digits'
    },
    'email': {
        'required': False,
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'description': 'Valid email format required'
    },
    'phone': {
        'required': False,
        'pattern': r'^\+?1?\d{10,15}$',
        'description': 'Valid phone number format'
    },
    'license_number': {
        'required': False,
        'pattern': r'^[A-Z0-9]{5,20}$',
        'description': 'License number format'
    }
}

# Matching Configuration
MATCHING_CONFIG = {
    'thresholds': {
        'exact_match': 1.0,
        'high_confidence': 0.85,
        'medium_confidence': 0.70,
        'low_confidence': 0.50
    },
    'weights': {
        'npi': 0.40,
        'name': 0.25,
        'license_number': 0.20,
        'email': 0.10,
        'phone': 0.05
    },
    'fuzzy_matching': {
        'enabled': True,
        'algorithm': 'levenshtein',
        'threshold': 0.80
    }
}

# Graph Schema Configuration
GRAPH_CONSTRAINTS = [
    "CREATE CONSTRAINT provider_npi IF NOT EXISTS FOR (p:Provider) REQUIRE p.npi IS UNIQUE",
    "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
    "CREATE CONSTRAINT specialty_code IF NOT EXISTS FOR (s:Specialty) REQUIRE s.specialty_code IS UNIQUE",
    "CREATE CONSTRAINT credential_id IF NOT EXISTS FOR (c:Credential) REQUIRE c.credential_id IS UNIQUE"
]

GRAPH_INDEXES = [
    "CREATE INDEX provider_name IF NOT EXISTS FOR (p:Provider) ON (p.last_name, p.first_name)",
    "CREATE INDEX provider_email IF NOT EXISTS FOR (p:Provider) ON (p.email)",
    "CREATE INDEX location_address IF NOT EXISTS FOR (l:Location) ON (l.address)"
]

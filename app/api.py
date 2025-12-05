"""
FastAPI application for Provider MDM.
Exposes endpoints for provider matching.
"""
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .config import Neo4jConnection
from .engine import ProviderMDMEngine
from .models import Provider, MatchResult

# Global engine instance
engine: ProviderMDMEngine = None
conn: Neo4jConnection = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection lifecycle."""
    global engine, conn
    conn = Neo4jConnection()
    conn.connect()
    engine = ProviderMDMEngine(conn)
    print("Neo4j connection established.")
    yield
    conn.close()
    print("Neo4j connection closed.")

app = FastAPI(title="Provider MDM API", lifespan=lifespan)

@app.post("/match", response_model=List[MatchResult])
async def match_provider(provider: Provider):
    """
    Match an incoming provider against the existing graph.
    Returns a list of potential matches with scores.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Database connection not initialized")
    
    try:
        matches = engine.match_providers(provider)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

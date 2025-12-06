"""
FastAPI application for Provider MDM.
Exposes endpoints for provider matching.
"""
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import Neo4jConnection
from .engine import ProviderMDMEngine
from .models import Provider, MatchResult, MergeRequest

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

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. In prod, specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search", response_model=List[Provider])
async def search_providers(q: str = Query(..., min_length=2)):
    """Search providers by name or other attributes."""
    if not engine:
        raise HTTPException(status_code=503, detail="Database connection not initialized")
    results = engine.search_providers(q)
    return results

@app.get("/providers/{npi}", response_model=Provider)
async def get_provider(npi: str):
    """Get full provider details by NPI."""
    if not engine:
        raise HTTPException(status_code=503, detail="Database connection not initialized")
    provider = engine.get_provider(npi)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

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

@app.post("/merge", response_model=Provider)
async def merge_providers(request: MergeRequest):
    """
    Merge source providers into a target provider to create a Golden Record.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Database connection not initialized")
    
    # Simple validation
    if request.target_npi in request.source_npis:
        raise HTTPException(status_code=400, detail="Target NPI cannot be in source NPIs")
        
    try:
        engine.merge_providers(request.target_npi, request.source_npis)
        # Return the updated target provider
        updated_provider = engine.get_provider(request.target_npi)
        if not updated_provider:
             raise HTTPException(status_code=500, detail="Failed to retrieve updated provider after merge")
        return updated_provider
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

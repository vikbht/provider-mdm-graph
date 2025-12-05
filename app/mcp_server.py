"""
MCP Server for Provider MDM.
Exposes graph capabilities to LLM agents.
"""
import asyncio
import json
import logging
import sys
import os
from typing import Optional, List, Dict, Any

# Ensure app module is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server import Server
import mcp.types as types
from mcp.server.stdio import stdio_server
from app.config import Neo4jConnection
from app.engine import ProviderMDMEngine
from app.models import Provider

# Initialize Server
app = Server("provider-mdm")

# Global engine instance
conn: Optional[Neo4jConnection] = None
engine: Optional[ProviderMDMEngine] = None

def get_engine() -> ProviderMDMEngine:
    global conn, engine
    if not engine:
        conn = Neo4jConnection()
        conn.connect()
        engine = ProviderMDMEngine(conn)
    return engine

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_providers",
            description="Search for healthcare providers by name, email, or other attributes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search text"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_provider_details",
            description="Retrieve full details for a specific provider by NPI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "npi": {"type": "string", "description": "National Provider Identifier"}
                },
                "required": ["npi"]
            }
        ),
        types.Tool(
            name="match_provider",
            description="Check if a candidate provider matches existing records (duplicates).",
            inputSchema={
                "type": "object",
                "properties": {
                    "npi": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "license_number": {"type": "string"}
                },
                "required": ["npi", "first_name", "last_name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    engine = get_engine()
    
    if name == "search_providers":
        query = arguments.get("query")
        results = engine.search_providers(query)
        return [types.TextContent(type="text", text=json.dumps(results, indent=2, default=str))]
    
    elif name == "get_provider_details":
        npi = arguments.get("npi")
        provider = engine.get_provider(npi)
        if not provider:
            return [types.TextContent(type="text", text=f"No provider found with NPI: {npi}")]
        return [types.TextContent(type="text", text=json.dumps(provider, indent=2, default=str))]
        
    elif name == "match_provider":
        candidate = Provider(**arguments)
        matches = engine.match_providers(candidate)
        output = []
        for m in matches:
            output.append({
                "target_npi": m.provider2_npi,
                "score": m.match_score,
                "type": m.match_type,
                "recommendation": m.recommended_action
            })
        return [types.TextContent(type="text", text=json.dumps(output, indent=2))]
    
    raise ValueError(f"Unknown tool: {name}")

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    # In a real app we might list all providers, but that's too many.
    # We expose a URL pattern essentially.
    return []

@app.read_resource()
async def read_resource(uri: Any) -> str | bytes:
    # URI format: provider://{npi}
    uri_str = str(uri)
    if not uri_str.startswith("provider://"):
        raise ValueError("Invalid resource URI")
    
    npi = uri_str.split("provider://")[1]
    engine = get_engine()
    provider = engine.get_provider(npi)
    if not provider:
        raise ValueError(f"Provider {npi} not found")
        
    return json.dumps(provider, indent=2, default=str)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        if conn:
            conn.close()

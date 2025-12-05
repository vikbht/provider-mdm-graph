# MCP Server Guide

This project exposes a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that allows LLM agents (like Claude Desktop) to interact with the Provider MDM graph.

## Capabilities
The server exposes the following tools:
1.  **`search_providers(query)`**: Fuzzy search for providers.
2.  **`get_provider_details(npi)`**: Get full graph details for a provider.
3.  **`match_provider(candidate)`**: Check for duplicates against the graph using the MDM engine.

## Configuration

### Using with Claude Desktop

Add the following to your Claude Desktop configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "provider-mdm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/provider-mdm-graph",
        "provider-mcp"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password_here"
      }
    }
  }
}
```

> **Note**: Replace `/absolute/path/to/provider-mdm-graph` with the actual path to your cloned repository.

### Running Manually
You can run the server over stdio for testing:
```bash
uv run provider-mcp
```

### Interactive CLI (No Claude/Node required)
A custom Python CLI is included to interact with the server directly from your terminal:

```bash
uv run provider-mcp-cli
```

This tool allows you to list tools, select them, and input arguments as JSON to see real-time results.

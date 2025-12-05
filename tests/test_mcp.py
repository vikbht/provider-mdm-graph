"""
Verification script for MCP Server.
"""
import sys
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

async def main():
    print("Starting MCP Server verification...")
    
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "app/mcp_server.py"],
        env=os.environ.copy()
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List Tools
            tools = await session.list_tools()
            print(f"\nDiscovered {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f" - {tool.name}: {tool.description}")
            
            if len(tools.tools) >= 3:
                print("\nVERIFICATION PASSED: Expected tools found.")
            else:
                print("\nVERIFICATION FAILED: Missing tools.")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

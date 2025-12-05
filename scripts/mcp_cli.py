"""
Interactive CLI Client for MCP Server.
Allows manual interaction with the provider-mcp server.
"""
import asyncio
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def interact(session: ClientSession):
    print("\n=== Provider MDM MCP Client ===")
    print("Connected to server.")
    
    while True:
        try:
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print("\nAvailable Tools:")
            for i, tool in enumerate(tools):
                print(f"{i + 1}. {tool.name}")
                # print(f"   {tool.description[:60]}...")
            print("q. Quit")
            
            choice = input("\nSelect a tool (number) or 'q': ").strip()
            if choice.lower() == 'q':
                break
                
            try:
                idx = int(choice) - 1
                if not (0 <= idx < len(tools)):
                    print("Invalid selection.")
                    continue
                    
                tool = tools[idx]
                print(f"\n--- {tool.name} ---")
                print(f"Description: {tool.description}")
                print(f"Input Schema: {json.dumps(tool.inputSchema, indent=2)}")
                
                print("\nEnter arguments as JSON (e.g. {\"query\": \"smith\"}).")
                print("Press Enter with empty text to send empty object {}.")
                args_str = input("> ").strip()
                
                if not args_str:
                    args = {}
                else:
                    try:
                        args = json.loads(args_str)
                    except json.JSONDecodeError:
                        print("Error: Invalid JSON format.")
                        continue
                    
                print("\nCalling tool...")
                result = await session.call_tool(tool.name, arguments=args)
                
                print("\n=== RESULT ===")
                for content in result.content:
                    if content.type == "text":
                        print(content.text)
                    else:
                        print(f"[{content.type} content]")
                print("==============")
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print(f"Error invoking tool: {e}")
                
        except Exception as e:
            print(f"Session error: {e}")
            break

async def main():
    # Detect if we are running in the project root to find the command correctly
    # We assume 'uv' is available and 'provider-mcp' script is registered/available via uv run
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "provider-mcp"],
        env=os.environ.copy()
    )
    
    print("Connecting to MCP server...")
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await interact(session)
    except Exception as e:
        print(f"\nFailed to connect to MCP server: {e}")
        print("Ensure 'uv run provider-mcp' works manually.")

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    run()

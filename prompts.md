# User Prompts History

This document chronicles the development journey of the **Provider MDM Graph** application, capturing the user's intent at each phase.

*Note: Early prompts are reconstructed from project milestones and completed tasks.*

## Phase 1: Foundation & Refactoring
**Likely Prompt:** "Analyze the current codebase and help me reorganize it into a proper Python package structure. Move scripts, tests, and app code into dedicated directories."

*   **Outcome**: Created `app/`, `scripts/`, `tests/` directories; updated imports; created `Dockerfile` and `docker-compose.yml`.

## Phase 2: Agent Integration (MCP)
**Likely Prompt:** "I want to enable AI agents to interact with this database. Implement a Model Context Protocol (MCP) server that exposes searching and matching tools."

*   **Outcome**: Created `app/mcp_server.py` with `search_providers` and `match_providers` tools.

## Phase 3: Interactive Tools
**Likely Prompt:** "Build a CLI client so I can test the MCP server manually without an agent."

*   **Outcome**: Developed `scripts/mcp_cli.py` for interactive testing of the MCP tools.

## Phase 4: Web Frontend & API (Current Session)
**Actual Prompt:** "Match & Deddupe is not working. Launch a brower to verify"
*   **Context**: Debugging the initial React frontend implementation.

**Actual Prompt:** "how would i implement the merge logic to generate a golden record"
*   **Outcome**: Designed the "Link & Flag" merge strategy and implemented `POST /merge` endpoint.

**Actual Prompt:** "run it for me"
*   **Context**: Requested a demonstration of the new Merge feature using the browser automation.

**Actual Prompt:** "update all necessary documentation files with the new capabilities developed"
*   **Outcome**: Updated `README.md`, `API_GUIDE.md`, and `EXECUTION_GUIDE.md` to include all new features.

**Actual Prompt:** "can you gather up all the prompts i have issued in building out this application and put them into a readme file."
*   **Outcome**: This document.

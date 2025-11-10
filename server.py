"""
Minimal MCP server exposing a single tool `read_projects`
with optional Bearer Token or Basic Auth support.

The tool performs an HTTP GET against a configurable upstream projects service
and returns the JSON body.

Authentication:
---------------
- If PROJECTS_API_TOKEN is set → Uses Bearer token
- Else if PROJECTS_API_USER & PROJECTS_API_PASSWORD are set → Uses Basic Auth
- Else → No authentication (will raise 500 error)

Environment Variables:
----------------------
    PROJECTS_SERVICE_URL    Base URL of the upstream service
                            (default: http://localhost:9000/internal-api/project-service/v1)
    PROJECTS_API_USER       Basic auth username (optional)
    PROJECTS_API_PASSWORD   Basic auth password (optional)
    PROJECTS_API_TOKEN      Bearer token (optional)

Run:
    uv run python server.py

Test:
    echo '{"method":"tools/list","jsonrpc":"2.0","id":1}' | uv run python server.py
"""

from __future__ import annotations
import os
from typing import Optional, Any

import httpx
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP  # FastMCP v2
import asyncio
import uvicorn
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Load configuration
# -----------------------------------------------------------------------------
load_dotenv()

# Instantiate MCP and FastAPI
mcp = FastMCP("procplan-mcp-server")

app = FastAPI(
    title="Procplan Projects - MCP Server",
    description="Procurement Planning MCP server exposing 'read_projects' tool "
                "with Basic Auth or Bearer Token support"
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "Procplan Projects MCP server is running", "tool": "read_projects"}


# -----------------------------------------------------------------------------
# MCP Tool Implementation
# -----------------------------------------------------------------------------
@mcp.tool
async def read_projects(project_id: Optional[str] = None) -> dict[str, Any]:
    """
    Read project data from the upstream projects API.

    Automatically chooses between Bearer Token and Basic Auth
    depending on environment variables.

    Parameters
    ----------
    project_id: Optional[str]
        If provided fetch a single project (/Projects('<id>')),
        otherwise fetch the collection (/Projects).

    Returns
    -------
    dict[str, Any]
        Parsed JSON payload from the upstream service.
    """

    base_url = os.getenv(
        "PROJECTS_SERVICE_URL",
        "http://localhost:9000/internal-api/project-service/v1"
    ).rstrip("/")

    # --- Authentication mode ---
    token = os.getenv("PROJECTS_API_TOKEN")
    username = os.getenv("PROJECTS_API_USER")
    password = os.getenv("PROJECTS_API_PASSWORD")

    headers = {}
    auth = None

    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif username and password:
        auth = httpx.BasicAuth(username, password)
    else:
        raise HTTPException(
            status_code=500,
            detail="Missing authentication: set PROJECTS_API_TOKEN or "
                   "PROJECTS_API_USER / PROJECTS_API_PASSWORD in .env"
        )

    # --- Request URL ---
    path = f"/Projects('{project_id}')" if project_id else "/Projects"
    url = f"{base_url}{path}"

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0), auth=auth, headers=headers) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            # Wrap in a consistent envelope if upstream returns a list directly
            if isinstance(data, list):
                return {"projects": data, "count": len(data)}
            return data

        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error fetching from {base_url}: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
def main() -> None:
    """Run both FastAPI (HTTP) and MCP servers together."""
    async def run_all():
        # Run FastAPI HTTP server (for REST access)
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        # Run MCP server concurrently
        await asyncio.gather(server.serve(), asyncio.to_thread(mcp.run))
    
    asyncio.run(run_all())


if __name__ == "__main__":
    main()

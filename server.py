"""Minimal MCP server exposing a single tool `read_projects`.

Uses the `mcp` fast server helper. The tool performs an HTTP GET against a
configurable upstream projects service and returns the JSON body.

Environment Variables:
	PROJECTS_SERVICE_URL  Base URL of the upstream service (default http://localhost:5001)

Example upstream endpoints expected:
	GET /projects              -> list of projects
	GET /projects/<project_id> -> single project

Run:
	uv run python server.py    # starts MCP server over stdio

Test (manual):
	echo '{"method":"tools/list","jsonrpc":"2.0","id":1}' | uv run python server.py

"""

from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()
from typing import Optional, Any
from fastapi import FastAPI, HTTPException
import httpx
from fastmcp import FastMCP  # FastMCP v2 import

# Instantiate FastMCP v2 server
mcp = FastMCP("procplan-mcp-server")


@mcp.tool
async def read_projects(project_id: Optional[str] = None) -> dict[str, Any]:
		"""Read project data from the upstream projects API.

		Parameters
		----------
		project_id: Optional[str]
				If provided fetch a single project (/projects/<id>), otherwise fetch the
				collection (/projects).

		Returns
		-------
		dict[str, Any]
				Parsed JSON payload from the upstream service.

		Error Handling
		--------------
		- Network errors or non-2xx responses raise an exception which the MCP
			framework returns as a tool call error.
		"""
		base = os.getenv("PROJECTS_SERVICE_URL", "http://localhost:5001")
		base = base.rstrip("/")
		path = f"/projects/{project_id}" if project_id else "/projects"
		url = f"{base}{path}"

		async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
				resp = await client.get(url)
				resp.raise_for_status()
				data = resp.json()

		# Wrap in a consistent envelope if upstream returns a list directly
		if isinstance(data, list):
				return {"projects": data, "count": len(data)}
		return data


def main() -> None:  # pragma: no cover - thin wrapper
	"""Run the FastMCP v2 server over stdio."""
	mcp.run()


if __name__ == "__main__":  # pragma: no cover
	main()


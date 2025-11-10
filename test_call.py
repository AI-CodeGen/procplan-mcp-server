"""Ad-hoc test script for the MCP server's read_projects tool.

Run examples:
  uv run python test_call.py                 # list projects
  PROJECT_ID=123 uv run python test_call.py  # fetch project 123
"""

from __future__ import annotations

import asyncio
import os

from server import read_projects  # type: ignore


async def _main() -> None:
    project_id = os.getenv("PROJECT_ID")
    data = await read_projects(project_id=project_id)
    print(data)


if __name__ == "__main__":
    asyncio.run(_main())

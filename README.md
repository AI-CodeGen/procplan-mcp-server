## procplan-mcp-server

Minimal MCP server exposing a single tool `read_projects` that proxies to a local (or remote) Projects REST service.

> Upgraded to **FastMCP v2** – using the modern `from fastmcp import FastMCP` import and `@mcp.tool` decorator style. Earlier examples that used `from mcp.server.fastmcp import FastMCP` or `@server.tool()` are now deprecated here.

### Tool: read_projects
Inputs:
- project_id (optional, string): If supplied fetches `/projects/<id>`, otherwise `/projects`.

Output:
- JSON object: If upstream returned a list it is wrapped as `{ "projects": [...], "count": N }`, otherwise the JSON is passed through.

### Environment Variables
- `PROJECTS_SERVICE_URL` (default: `http://localhost:5001`)

`server.py` calls `load_dotenv()` at import time, so a local `.env` file in the project root will be read automatically.

#### Ways to set `PROJECTS_SERVICE_URL`

1. Inline per command (fastest):
	```bash
	PROJECTS_SERVICE_URL="http://localhost:5005" uv run python server.py
	```
2. Export in current shell session:
	```bash
	export PROJECTS_SERVICE_URL="http://localhost:5005"
	uv run python server.py
	```
3. `.env` file (auto-loaded):
	```env
	PROJECTS_SERVICE_URL=http://localhost:5005
	```
4. Wrapper script (`run.sh`):
	```bash
	#!/usr/bin/env bash
	export PROJECTS_SERVICE_URL="http://projects:5005"
	uv run python server.py
	```
5. Docker / Compose:
	```yaml
	services:
	  mcp-server:
		 image: your-image
		 environment:
			PROJECTS_SERVICE_URL: http://projects:5005
	```
6. systemd service (Linux):
	```ini
	[Service]
	Environment=PROJECTS_SERVICE_URL=http://projects:5005
	ExecStart=/usr/bin/uv run python /opt/procplan-mcp-server/server.py
	```
7. Client integration (MCP host app): configure env before spawning the process.

If unset, the server falls back to `http://localhost:5001`.

### Expected Upstream API
```
GET /projects            -> 200 JSON list
GET /projects/<id>       -> 200 JSON object
```

### Run the Server (stdio)
```bash
uv run python server.py
```

### Install / Sync Dependencies
After cloning or changing dependencies:
```bash
uv sync           # installs fastmcp, httpx, dotenv (stdlib usage only) per pyproject.toml
```

If you previously used the legacy SDK:
```bash
uv remove mcp[cli]
uv add fastmcp>=2.0.0
```

### List Tools (manual test)
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | uv run python server.py
```

### Call Tool (list projects)
```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_projects","arguments":{}}}' | uv run python server.py
```

### Call Tool (single project)
```bash
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"read_projects","arguments":{"project_id":"123"}}}' | uv run python server.py
```

### Add Dependency / Lock Update
```bash
uv add httpx
```

### Notes
- Uses `mcp[cli]` fast server helper (`FastMCP`).
- Network timeouts set to 10s.
- Non-2xx responses surface as tool errors to the client.

### FastMCP v2 Differences
- Import path: `from fastmcp import FastMCP`
- Decorator style: `@mcp.tool` vs older `@server.tool()`
- Same `mcp.run()` entry point for stdio execution
- Designed for richer ecosystem (composition, auth, proxies). This project only uses the minimal tool exposure.

### Upgrade Checklist (from older implementation)
1. Replace legacy import with `from fastmcp import FastMCP`
2. Rename instance variable (e.g. `server` -> `mcp` for clarity)
3. Change decorators to `@mcp.tool`
4. Update dependency in `pyproject.toml`
5. Run `uv sync`
6. (Optional) Add new tools / resources using FastMCP 2.x patterns

### Planned Enhancements (Optional)
- Add a `search_projects` tool with query filtering
- Introduce retries & exponential backoff for transient upstream failures
- Add JSON schema validation of upstream responses
- Provide OpenAPI-like resource exposure using FastMCP composition patterns



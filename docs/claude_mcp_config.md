# 🧩 Adding an MCP Server to Claude Desktop

This guide explains how to configure the **Claude Desktop Client** to connect to your local **MCP server**.

**Prerequisite:**
1. Claude Desktop Client must be installed.
2. Then open it and add config in Settings -> Developer so that you can edit the claude_desktop_config.json file.

---

## ⚙️ Configuration

Add the following block to your Claude Desktop configuration file:

**File path (macOS):**
~/Library/Application Support/Claude/claude_desktop_config.json

**JSON Config:**
```json
{
  "preferences": {
    "quickEntryDictationShortcut": "capslock"
  },
  "mcpServers": {
    "procplan-mcp-server": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "--directory",
        "/Users/I570218/Documents/GitHub/procplan-mcp-server",
        "run",
        "python",
        "server.py"
      ],
      "stdio": "pipe",
      "env": {
        "PROJECTS_SERVICE_URL": "http://localhost:9000/internal-api/project-service/v1",
        "PROJECTS_API_USER": "admin-test-user",
        "PROJECTS_API_PASSWORD": "test-password"
      }
    }
  }
}
```

## Why and How is this configuration
⚙️ **1. When Claude runs “directly in .venv”**

If your config looked like this:

"command": "/Users/I570218/Documents/GitHub/procplan-mcp-server/.venv/bin/python",
"args": ["server.py"]


Then Claude would:

Spawn your virtual environment’s Python interpreter directly.

Use whatever environment is active in .venv at that time.

This works fine — but you are responsible for ensuring dependencies are installed and synced (pip install, uv sync, etc.).

Claude can’t automatically manage or reproduce that environment if you share it with someone else or move it to another machine.

🧩 So: direct .venv execution = “manual environment management” mode.

🚀 **2. When Claude runs via uv --directory ... run python server.py**

In this mode:

uv acts as a smart environment runner — it automatically finds your pyproject.toml and .venv.

It guarantees the dependencies listed in your project are available (or installs them on demand).

It uses the project root (--directory ...) to locate .venv and .python-version.

So it’s environment-aware, reproducible, and consistent — even when Claude runs it from a clean environment.

🧩 This is “reproducible managed environment” mode — preferred for tools like MCP, CI, and IDE integration.
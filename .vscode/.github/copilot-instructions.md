# Copilot Instructions for MCP Server Project

This repository implements an MCP (Model Context Protocol) server.

## Important Docs
- The folder `./docs/` contains all relevant MCP specifications and guidelines.
- These include `intro.md`, `mcp-architecture.md`, `build-server.md`, `fastmcp-server-v2.md`, and others from the official Model Context Protocol website.

## Guidance for Copilot
When generating or suggesting code:
- Follow the protocol rules as described in the docs.
- Use examples and schema details from `docs/*`.
- Assume this server follows the MCP spec exactly.
- This project uses `uv` as package manager.

## Example Prompts
- “Refer to `docs/mcp-architecture.md`, to understand basics of MCP server.”
- “Refer to `docs/build-server.md` and `docs/fastmcp-server-v2.md` to build an mcp server.”

# Vibe Coding Mode
When coding in this project, always:
- Reference docs under `../docs/` for MCP-specific behaviors.
- Suggest structured code following the protocol schema.
- Keep responses concise and aligned with the official spec.

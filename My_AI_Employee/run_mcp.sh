#!/bin/bash
# Wrapper script to run MCP servers from the correct directory
cd "$(dirname "$0")"
uv run python -m "src.my_ai_employee.mcp_servers.$1"

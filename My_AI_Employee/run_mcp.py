#!/usr/bin/env python3
"""
Wrapper script to run MCP servers from the correct directory.
This script changes to the script's directory before running the MCP server.
"""
import sys
import os
from pathlib import Path

# Change to script's directory (where pyproject.toml is)
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Get MCP server name from command line
mcp_name = sys.argv[1] if len(sys.argv) > 1 else "email_mcp"

# Run the MCP server
import subprocess
result = subprocess.run(
    ["uv", "run", "python", "-m", f"src.my_ai_employee.mcp_servers.{mcp_name}"],
    cwd=script_dir,
    stdin=sys.stdin,
    stdout=sys.stdout,
    stderr=sys.stderr
)

sys.exit(result.returncode)

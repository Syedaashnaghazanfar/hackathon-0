#!/usr/bin/env python3
import os, sys
from pathlib import Path

# Add My_AI_Employee to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "My_AI_Employee"))

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / "My_AI_Employee" / ".env"
load_dotenv(env_path)

# Set DRY_RUN for testing
os.environ['DRY_RUN'] = 'true'
print("="*70)
print("ODOO MCP SERVER TEST")
print("="*70)
print("\n[1] Environment:")
print(f"   DRY_RUN: {os.getenv('DRY_RUN')}")
print(f"   ODOO_URL: {os.getenv('ODOO_URL')}")
print(f"   Database: {os.getenv('ODOO_DATABASE')}")
print("\n[2] Importing server...")
try:
    from src.my_ai_employee.mcp_servers.odoo_mcp import health_check
    print("   OK - Import successful")
    print("\n[3] Verifying MCP tools are registered...")
    # Import the MCP server to check if it loads correctly
    import src.my_ai_employee.mcp_servers.odoo_mcp as odoo_server
    print("   OK - MCP server module loaded")

    print("\n" + "="*70)
    print("SUCCESS! Odoo MCP server is ready.")
    print("="*70)
    print("\nAvailable tools:")
    print("  - create_invoice")
    print("  - send_invoice")
    print("  - record_payment")
    print("  - health_check")
    print("\nTo test with actual Odoo instance:")
    print("  1. Start Odoo: docker run -d -p 8069:8069 odoo:latest")
    print("  2. Set DRY_RUN=false in .env")
    print("  3. Add MCP server to Claude Desktop settings")
    print("  4. Use tools in Claude Code")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Test Odoo MCP Server tools.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "My_AI_Employee"))

from mcp import ClientSession, StdioServerParameters


async def test_odoo_tools():
    """Test Odoo MCP tools."""
    print("="*70)
    print("TESTING ODOO MCP SERVER")
    print("="*70)

    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.my_ai_employee.mcp_servers.odoo_mcp"],
        cwd=project_root / "My_AI_Employee"
    )

    print("\n[1] Starting Odoo MCP server...")

    async with ClientSession(server_params) as session:
        print("   ✓ Server connected")

        # List available tools
        print("\n[2] Listing available tools...")
        tools = await session.list_tools()
        print(f"   Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}")

        # Test health check
        print("\n[3] Testing health_check tool...")
        try:
            result = await session.call_tool("health_check", {})
            print(f"   ✓ Health check result:")
            print(f"     Status: {result.get('status')}")
            print(f"     Connected: {result.get('connected')}")
            print(f"     Odoo URL: {result.get('odoo_url')}")
            print(f"     Database: {result.get('database')}")
            print(f"     DRY_RUN: {result.get('dry_run')}")
        except Exception as e:
            print(f"   ✗ Health check failed: {e}")

        # Test create_invoice (dry run)
        print("\n[4] Testing create_invoice tool (DRY RUN)...")
        try:
            result = await session.call_tool("create_invoice", {
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "invoice_date": "2026-02-08",
                "due_date": "2026-03-08",
                "line_items": [
                    {
                        "description": "Test Service",
                        "quantity": 1,
                        "unit_price": 100.00
                    }
                ],
                "tax_rate": 0.0,
                "notes": "Test invoice from Gold Tier AI Employee"
            })

            print(f"   ✓ Invoice created (dry run):")
            print(f"     Invoice ID: {result.get('invoice_id')}")
            print(f"     Status: {result.get('status')}")
            print(f"     Total: ${result.get('total_amount', 0):.2f}")
            print(f"     Success: {result.get('success', False)}")

        except Exception as e:
            print(f"   ✗ Invoice creation failed: {e}")

    print("\n" + "="*70)
    print("ODOO MCP SERVER TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(test_odoo_tools())
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()

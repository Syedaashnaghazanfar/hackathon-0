#!/usr/bin/env python3
"""
Test Odoo MCP Server with actual Odoo instance.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "My_AI_Employee"
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Set DRY_RUN to false to test actual connection
os.environ['DRY_RUN'] = 'false'

print("=" * 80)
print("ODOO MCP SERVER - REAL CONNECTION TEST")
print("=" * 80)

print("\n[1] Configuration:")
print(f"   ODOO_URL: {os.getenv('ODOO_URL')}")
print(f"   ODOO_DATABASE: {os.getenv('ODOO_DATABASE')}")
print(f"   ODOO_USERNAME: {os.getenv('ODOO_USERNAME')}")
print(f"   DRY_RUN: {os.getenv('DRY_RUN')}")

print("\n[2] Testing OdooRPC Connection...")
try:
    import odoorpc
    print("   odoorpc library installed: OK")

    # Try to connect to Odoo
    print("\n[3] Attempting to connect to Odoo...")
    odoo_url = os.getenv('ODOO_URL', 'localhost')
    # Remove http:// or https:// prefix and port
    if '://' in odoo_url:
        odoo_url = odoo_url.split('://')[1]
    if ':' in odoo_url:
        odoo_url = odoo_url.split(':')[0]

    print(f"   Connecting to: {odoo_url}:8069")
    odoo = odoorpc.ODOO(odoo_url, port=8069)

    print("   Connection established: YES")
    print(f"   Odoo version: {odoo.version}")

    # List databases
    print("\n[4] Available databases:")
    try:
        databases = odoo.db.list()
        print(f"   Found {len(databases)} database(s):")
        for db in databases:
            print(f"   - {db}")
    except Exception as e:
        print(f"   Error listing databases: {e}")

    # Check if our target database exists and is initialized
    target_db = os.getenv('ODOO_DATABASE', 'odoo_db')
    print(f"\n[5] Checking database '{target_db}'...")

    try:
        # Try to login
        print(f"   Attempting login to '{target_db}'...")
        odoo.login(
            target_db,
            os.getenv('ODOO_USERNAME', 'admin'),
            os.getenv('ODOO_API_KEY', 'admin')
        )
        print("   ✅ LOGIN SUCCESSFUL!")
        print(f"   User: {odoo.env.user.name}")
        print(f"   Company: {odoo.env.user.company_id.name}")

        # Check if accounting module is installed
        print("\n[6] Checking installed modules...")
        modules = odoo.env['ir.module.module'].search_count([
            ('state', '=', 'installed'),
            ('name', 'in', ['account', 'sale_management', 'account_invoicing'])
        ])
        print(f"   Accounting-related modules installed: {modules}")

        # Test basic operations
        print("\n[7] Testing basic operations...")

        # Check if we can access models
        try:
            partners_count = odoo.env['res.partner'].search_count([])
            print(f"   Partners in database: {partners_count}")
        except Exception as e:
            print(f"   Cannot access partners: {e}")

        try:
            invoices_count = odoo.env['account.move'].search_count([])
            print(f"   Invoices in database: {invoices_count}")
        except Exception as e:
            print(f"   Cannot access invoices: {e}")

        print("\n[8] Odoo is ready for MCP Server!")
        print("   The database is initialized and accessible.")
        print("   You can now use the MCP tools to create invoices.")

    except Exception as e:
        print(f"   ❌ LOGIN FAILED: {e}")
        print("\n   This is expected for a fresh Odoo installation.")
        print("   You need to:")
        print("   1. Open http://localhost:8069 in your browser")
        print("   2. Click 'Manage Databases'")
        print("   3. Create a new database named 'odoo_db'")
        print("   4. Set admin email and password")
        print("   5. Wait for initialization to complete")
        print("   6. Update ODOO_API_KEY in .env with the admin password")
        print("   7. Run this test again")

except ImportError as e:
    print(f"   ERROR: {e}")
    print("   Install odoorpc: pip install odoorpc")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

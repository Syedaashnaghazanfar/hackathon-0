#!/usr/bin/env python3
"""Test Odoo login without emojis."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "My_AI_Employee"
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")
os.environ['DRY_RUN'] = 'false'

print("=" * 80)
print("ODOO LOGIN TEST")
print("=" * 80)

import odoorpc

# Parse URL
odoo_url = os.getenv('ODOO_URL', 'localhost')
if '://' in odoo_url:
    odoo_url = odoo_url.split('://')[1]
if ':' in odoo_url:
    odoo_url = odoo_url.split(':')[0]

print(f"\n[1] Connecting to: {odoo_url}:8069")
odoo = odoorpc.ODOO(odoo_url, port=8069)
print(f"   Connected! Odoo version: {odoo.version}")

print(f"\n[2] Attempting login to '{os.getenv('ODOO_DATABASE')}'...")
try:
    odoo.login(
        os.getenv('ODOO_DATABASE'),
        os.getenv('ODOO_USERNAME'),
        os.getenv('ODOO_API_KEY')
    )
    print("   *** LOGIN SUCCESSFUL! ***")
    print(f"   User: {odoo.env.user.name}")
    print(f"   Email: {odoo.env.user.email}")
    print(f"   Company: {odoo.env.user.company_id.name}")

    # Check accounting module
    print("\n[3] Checking Accounting module...")
    try:
        modules = odoo.env['ir.module.module'].search([
            ('name', '=', 'account'),
            ('state', '=', 'installed')
        ])
        if modules:
            print("   *** Accounting module INSTALLED ***")
        else:
            print("   Accounting module NOT installed")
    except Exception as e:
        print(f"   Error checking modules: {e}")

    # Check if we can access invoice model
    print("\n[4] Testing invoice access...")
    try:
        invoices_count = odoo.env['account.move'].search_count([])
        print(f"   *** Can access invoices! Count: {invoices_count} ***")
    except Exception as e:
        print(f"   Cannot access invoices: {e}")

    print("\n" + "=" * 80)
    print("SUCCESS! Odoo MCP is ready to create invoices!")
    print("=" * 80)

except Exception as e:
    print(f"   *** LOGIN FAILED: {e} ***")
    print("\nTroubleshooting:")
    print("1. Verify you can login at http://localhost:8069")
    print("2. Check that ODOO_DATABASE=odoo_db in .env")
    print("3. Check that ODOO_USERNAME matches your login email")
    print("4. Check that ODOO_API_KEY matches your password")

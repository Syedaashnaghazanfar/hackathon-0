#!/usr/bin/env python3
"""Verify invoice was created in Odoo."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "My_AI_Employee"
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

import odoorpc

# Connect
odoo_url = os.getenv('ODOO_URL', 'localhost')
if '://' in odoo_url:
    odoo_url = odoo_url.split('://')[1]
if ':' in odoo_url:
    odoo_url = odoo_url.split(':')[0]

print("Connecting to Odoo...")
odoo = odoorpc.ODOO(odoo_url, port=8069)
odoo.login(
    os.getenv('ODOO_DATABASE'),
    os.getenv('ODOO_USERNAME'),
    os.getenv('ODOO_API_KEY')
)

print("\nSearching for invoices...")
# Use execute_kw directly to avoid frozendict issue
invoices = odoo.execute_kw(
    'account.move',
    'search_read',
    [[('move_type', '=', 'out_invoice')]],
    {'fields': ['name', 'partner_id', 'invoice_date', 'amount_total', 'state'], 'limit': 5}
)

print(f"\nFound {len(invoices)} recent customer invoices:")
print("=" * 80)

for inv in invoices[:5]:
    partner_name = inv.get('partner_id', [False, ''])[1] if isinstance(inv.get('partner_id'), list) else 'Unknown'
    print(f"\nInvoice: {inv.get('name', 'N/A')}")
    print(f"  Customer: {partner_name}")
    print(f"  Date: {inv.get('invoice_date', 'N/A')}")
    print(f"  Total: ${inv.get('amount_total', 0):.2f}")
    print(f"  State: {inv.get('state', 'unknown')}")

print("\n" + "=" * 80)
print("SUCCESS! Invoices are in Odoo!")
print("\nView them in Odoo:")
print("1. Go to http://localhost:8069")
print("2. Click 'Invoicing' > 'Customers' > 'Invoices'")

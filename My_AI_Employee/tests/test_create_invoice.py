#!/usr/bin/env python3
"""Create first test invoice via Odoo MCP."""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "My_AI_Employee"
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")
os.environ['DRY_RUN'] = 'false'

print("=" * 80)
print("CREATING FIRST INVOICE VIA ODOO MCP")
print("=" * 80)

import odoorpc

# Connect to Odoo
odoo_url = os.getenv('ODOO_URL', 'localhost')
if '://' in odoo_url:
    odoo_url = odoo_url.split('://')[1]
if ':' in odoo_url:
    odoo_url = odoo_url.split(':')[0]

print(f"\n[1] Connecting to Odoo at {odoo_url}:8069...")
odoo = odoorpc.ODOO(odoo_url, port=8069)
print(f"   Connected! Version: {odoo.version}")

print(f"\n[2] Logging in as {os.getenv('ODOO_USERNAME')}...")
odoo.login(
    os.getenv('ODOO_DATABASE'),
    os.getenv('ODOO_USERNAME'),
    os.getenv('ODOO_API_KEY')
)
print(f"   Logged in! User: {odoo.env.user.name}")

print("\n[3] Creating test invoice...")

# Search or create customer
print("   - Finding customer...")
Customer = odoo.env['res.partner']
customers = Customer.search([('name', '=', 'Test Customer')])

if customers:
    customer_id = customers[0]
    print(f"     Found existing customer: {Customer.browse(customer_id).name}")
else:
    print(f"     Creating new customer...")
    customer_id = Customer.create({
        'name': 'Test Customer',
        'email': 'test@example.com',
        'customer_rank': 1,
    })
    print(f"     Created customer ID: {customer_id}")

# Create invoice
print("\n   - Creating invoice line items...")
line_items = [
    (0, 0, {
        'name': 'Web Development Services',
        'quantity': 10.0,
        'price_unit': 150.00,
    }),
    (0, 0, {
        'name': 'Server Setup',
        'quantity': 1.0,
        'price_unit': 200.00,
    }),
]

print(f"     {len(line_items)} line items prepared")

# Prepare invoice values
invoice_vals = {
    'move_type': 'out_invoice',  # Customer invoice
    'partner_id': customer_id,
    'invoice_date': '2026-02-08',
    'invoice_line_ids': line_items,
}

print("\n   - Creating invoice...")
Invoice = odoo.env['account.move']
invoice_id = Invoice.create(invoice_vals)

print(f"\n   *** INVOICE CREATED! ID: {invoice_id} ***")

# Retrieve and display invoice
invoice = Invoice.browse(invoice_id)
print(f"\n[4] Invoice Details:")
print(f"   Invoice Number: {invoice.name}")
print(f"   Customer: {invoice.partner_id.name}")
print(f"   Date: {invoice.invoice_date}")
print(f"   Subtotal: ${invoice.amount_untaxed:.2f}")
print(f"   Tax: ${invoice.amount_tax:.2f}")
print(f"   Total: ${invoice.amount_total:.2f}")
print(f"   State: {invoice.state}")

print("\n" + "=" * 80)
print("SUCCESS! First invoice created via MCP!")
print("=" * 80)
print("\nYou can view this invoice in Odoo:")
print("1. Go to http://localhost:8069")
print("2. Click 'Accounting' or 'Invoicing' in the left menu")
print("3. Click 'Customers' > 'Invoices'")
print(f"4. Look for invoice: {invoice.name}")
print("\nNext step: Send invoice and record payment!")

# Odoo Integration - Next Steps

## Current Status: 🟡 ALMOST READY

### What's Working:
- ✅ PostgreSQL database running
- ✅ Odoo server running on http://localhost:8069
- ✅ Odoo MCP server fully implemented
- ✅ All utility modules tested and working
- ✅ Connection test script ready

### What's Needed:
- ⚠️ Initialize Odoo database via web interface (one-time setup)

---

## Step-by-Step Instructions

### Step 1: Initialize Odoo (One-Time Setup)

1. **Open Odoo in Browser:**
   ```
   http://localhost:8069
   ```

2. **Create Database:**
   - Click "Create Database"
   - Fill in the form:
     - **Database Name:** `odoo_db` (important: must match .env file!)
     - **Email:** your email address
     - **Password:** choose a strong password (remember this!)
     - **Language:** English
     - **Country:** your country
   - Click "Create"
   - Wait 5-10 minutes for initialization

3. **Verify Installation:**
   - Once complete, you'll see the Odoo dashboard
   - Go to Apps menu
   - Install "Accounting" app if not already installed
   - Install "Invoicing" app if not already installed

### Step 2: Configure MCP Server

Edit `My_AI_Employee/.env`:

```bash
# Update these with your actual credentials
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo_db          # Must match database name from Step 1
ODOO_USERNAME=admin            # Default admin username
ODOO_API_KEY=your_password     # Password you set in Step 1
ODOO_QUEUE_FILE=.odoo_queue.jsonl

# Enable production mode
DRY_RUN=false                  # Set to false to enable actual operations
```

### Step 3: Test Connection

After updating credentials, run:

```bash
python test_odoo_real_connection.py
```

Expected output:
```
[3] Attempting to connect to Odoo...
   Connecting to: localhost:8069
   ✅ LOGIN SUCCESSFUL!
   User: Administrator
   Company: Your Company
```

### Step 4: Create First Invoice (via MCP)

Once connection works, you can test creating invoices:

**Option A: Via Claude Code (Recommended)**
```python
# Use the create_invoice tool
create_invoice(
    customer_name="Test Customer",
    customer_email="test@example.com",
    invoice_date="2026-02-08",
    due_date="2026-03-08",
    line_items=[{
        "description": "Consulting Services",
        "quantity": 5,
        "unit_price": 150.00
    }],
    tax_rate=0.08
)
```

**Option B: Via Python Script**
```python
# Create test_invoice.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path("My_AI_Employee")))

from src.my_ai_employee.mcp_servers.odoo_mcp import create_invoice

# Create test invoice
result = await create_invoice(
    customer_name="Test Customer",
    customer_email="test@example.com",
    invoice_date="2026-02-08",
    due_date="2026-03-08",
    line_items=[{
        "description": "Consulting Services",
        "quantity": 5,
        "unit_price": 150.00
    }],
    tax_rate=0.08
)

print(f"Invoice created: {result}")
```

### Step 5: Add to Claude Desktop (Optional)

If you want to use the MCP server in Claude Desktop:

1. Edit `C:\Users\ashna\.claude.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["-m", "src.my_ai_employee.mcp_servers.odoo_mcp"],
      "cwd": "D:\\code\\Q4\\HACKATHON-ZERO\\My_AI_Employee\\My_AI_Employee",
      "env": {
        "DRY_RUN": "false",
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DATABASE": "odoo_db",
        "ODOO_USERNAME": "admin",
        "ODOO_API_KEY": "your_password",
        "ODOO_QUEUE_FILE": ".odoo_queue.jsonl"
      }
    }
  }
}
```

2. Restart Claude Desktop
3. The Odoo tools will be available in all conversations

---

## Troubleshooting

### Issue: "Database does not exist"
**Solution:** Make sure you created a database named exactly "odoo_db" in the Odoo web interface

### Issue: "Authentication failed"
**Solution:** Verify ODOO_USERNAME and ODOO_API_KEY in .env match what you set in the web interface

### Issue: "Relation does not exist" errors
**Solution:** The database wasn't initialized properly. Drop the database and recreate it:
```bash
docker exec db-postgres psql -U odoo -d postgres -c "DROP DATABASE odoo_db;"
docker exec db-postgres psql -U odoo -d postgres -c "DROP DATABASE odoo;"
```
Then repeat Step 1

### Issue: Can't access http://localhost:8069
**Solution:** Check if containers are running:
```bash
docker ps
```
You should see both "odoo" and "db-postgres" containers. If not, start them:
```bash
docker start db-postgres odoo
```

---

## Testing Checklist

After completing the setup, verify:

- [ ] Odoo web interface accessible at http://localhost:8069
- [ ] Can login to Odoo with admin credentials
- [ ] Accounting app is installed
- [ ] test_odoo_real_connection.py shows "LOGIN SUCCESSFUL"
- [ ] Can create invoice via MCP tool
- [ ] Invoice appears in Odoo Accounting > Invoices
- [ ] Can send invoice via MCP tool
- [ ] Can record payment via MCP tool

---

## Documentation

For more details, see:
- `ODOO_INTEGRATION_COMPLETE.md` - Technical implementation details
- `ODOO_TEST_RESULTS.md` - Comprehensive test results
- `GOLD_TIER_STATUS.md` - Overall Gold Tier progress

---

## Support

If you encounter issues:
1. Check Odoo logs: `docker logs odoo`
2. Check PostgreSQL logs: `docker logs db-postgres`
3. Verify database exists: `docker exec db-postgres psql -U odoo -d postgres -c "\l"`
4. Test connection: `python test_odoo_real_connection.py`

---

**Ready to automate your accounting with Odoo!** 🎉

Once you complete Step 1 (database initialization), the MCP server will be fully operational.

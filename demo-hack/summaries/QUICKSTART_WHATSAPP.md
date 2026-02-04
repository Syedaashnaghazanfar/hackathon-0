# WhatsApp Watcher - Quick Start Guide (CORRECTED PATHS)

Get WhatsApp watcher running in 5 minutes.

---

## Project Structure

```
My_AI_Employee/
├── .env                          # ← Your config file goes here
├── .whatsapp_session.json        # ← Created after QR scan
├── .whatsapp_dedupe.json         # ← Created automatically
├── AI_Employee_Vault/            # ← Vault folder (relative path)
│   ├── Needs_Action/
│   ├── Company_Handbook.md
│   └── ...
├── watchers/
│   └── whatsapp_watcher.py
└── pyproject.toml                # ← Dependencies (uses uv)
```

---

## Step 1: Install Dependencies (2 minutes)

**You use `uv` package manager (no requirements.txt needed):**

```bash
cd My_AI_Employee

# Install dependencies from pyproject.toml
uv pip install -e .

# Or if uv sync doesn't work:
uv pip install python-dotenv playwright watchdog python-frontmatter pydantic fastmcp google-api-python-client google-auth-oauthlib

# Install Playwright browser (REQUIRED)
playwright install chromium
```

**Alternative (if you don't have uv):**

```bash
pip install python-dotenv playwright watchdog python-frontmatter pydantic fastmcp google-api-python-client google-auth-oauthlib
playwright install chromium
```

---

## Step 2: Configure .env (1 minute)

**Create `My_AI_Employee/.env` file:**

```bash
cd My_AI_Employee

# Copy template
cp .env.whatsapp .env

# Or create manually:
cat > .env << 'EOF'
VAULT_PATH=AI_Employee_Vault
WHATSAPP_SESSION_FILE=.whatsapp_session.json
WHATSAPP_DEDUPE_FILE=.whatsapp_dedupe.json
WHATSAPP_WATCHER_INTERVAL=60
LOG_LEVEL=INFO
EOF
```

**IMPORTANT PATH NOTES:**
- `.env` is in `My_AI_Employee/` directory
- All paths are **relative to My_AI_Employee/** directory
- `VAULT_PATH=AI_Employee_Vault` (NOT `My_AI_Employee/AI_Employee_Vault`)
- Session files go in `My_AI_Employee/` (same directory as .env)

---

## Step 3: Initialize WhatsApp Session (1 minute)

```bash
cd My_AI_Employee

# Run initialization (ONE-TIME SETUP)
python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault
```

**What to do:**
1. Browser window opens with QR code
2. Open WhatsApp on your phone
3. Go to: **Settings → Linked Devices → Link a Device**
4. Scan the QR code
5. Wait for "QR code scanned successfully!" message

**Session saved to**: `My_AI_Employee/.whatsapp_session.json`

---

## Step 4: Run the Watcher (30 seconds)

```bash
cd My_AI_Employee

# Run watcher (keep terminal open)
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault
```

**You should see:**
```
INFO - WhatsApp watcher initialized
INFO - Monitoring 0 specific contacts (monitoring all)
INFO - WhatsApp session is active
INFO - Fetched 0 unread message previews from WhatsApp Web
```

**Keep this terminal open** - the watcher runs continuously.

---

## Step 5: Test It (1 minute)

### Test 1: Send Urgent Message

1. Send yourself: **"URGENT: Test message"**
2. Wait 60 seconds
3. Check: `My_AI_Employee/AI_Employee_Vault/Needs_Action/`
4. You should see: `YYYYMMDD_HHMMSS_whatsapp_YourName.md`

### Test 2: Check Priority

```bash
cd My_AI_Employee
ls -la AI_Employee_Vault/Needs_Action/
```

Open the created file and verify:
- **Priority**: High (because of "URGENT" keyword)
- **Message Preview**: Shows your test message
- **Formatting Notes**: Included at bottom

---

## Optional: Configure Monitored Contacts

Edit `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Monitored WhatsApp Contacts
- John Smith
- Sarah Johnson
- Important Client
```

**Restart watcher** to apply changes.

---

## Common Commands (All from My_AI_Employee/ directory)

```bash
cd My_AI_Employee

# Initialize session (first time only)
python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault

# Run watcher (normal operation)
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault

# Run in headless mode (no visible browser)
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault --headless

# Run with custom interval (check every 30 seconds)
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault --interval 30

# Show help
python -m watchers.whatsapp_watcher --help

# Run tests
pytest tests/integration/test_whatsapp_watcher.py -v

# Verify setup
bash test_whatsapp_setup.sh
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'playwright'"
```bash
cd My_AI_Employee
uv pip install playwright
playwright install chromium
```

### "WhatsApp session not found"
```bash
cd My_AI_Employee
python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault
```

### "QR code scan timeout"
- You have 2 minutes to scan
- Make sure phone has internet
- Try again with --init

### "No messages detected"
- Wait 60 seconds (default interval)
- Check if sender is in monitored contacts list
- Check logs for errors

### "FileNotFoundError: AI_Employee_Vault"
- Make sure you're in `My_AI_Employee/` directory
- Check that `AI_Employee_Vault/` folder exists
- Paths in .env are relative to `My_AI_Employee/`

---

## File Locations (CORRECTED)

```
My_AI_Employee/
├── .env                                    # Config file
├── .whatsapp_session.json                  # Session (after QR scan)
├── .whatsapp_dedupe.json                   # Dedupe tracker
├── AI_Employee_Vault/                      # Vault folder
│   ├── Needs_Action/                       # Action items created here
│   │   └── YYYYMMDD_HHMMSS_whatsapp_*.md
│   └── Company_Handbook.md                 # Monitored contacts
└── watchers/
    └── whatsapp_watcher.py
```

---

## What's Next?

1. ✅ WhatsApp watcher is running
2. Set up Gmail watcher for email monitoring
3. Set up LinkedIn watcher for notifications
4. Configure approval workflow for Silver tier
5. Set up MCP servers for executing actions

---

## Features Enabled

✅ **Preview-based reading** - Non-invasive, doesn't click into chats
✅ **Session expiration notification** - Creates action item when session expires
✅ **CLI --init flag** - Easy QR code setup
✅ **Monitored contacts filter** - Only track specific contacts
✅ **Improved priority logic** - Smart High/Medium priority based on keywords + unread count

---

**Need help?** See `WHATSAPP_SETUP_GUIDE.md` for detailed documentation.

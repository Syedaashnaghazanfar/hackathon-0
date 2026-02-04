# Gmail OAuth Setup Guide - Phase 9 (T093)

**Purpose**: Set up Gmail OAuth credentials for end-to-end testing

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Project name: `AI-Employee-Test` (or any name)
4. Click "Create"
5. Wait for project creation (30 seconds)

---

## Step 2: Enable Gmail API

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Gmail API"
4. Click "Enable"
5. Wait for API to be enabled (10 seconds)

---

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: `AI Employee Test`
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip (click "Save and Continue")
   - Test users: Add your Gmail address
   - Click "Save and Continue"
4. Back to "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: `AI Employee Desktop`
   - Click "Create"
5. Download credentials:
   - Click "Download JSON"
   - Save as `credentials.json`

---

## Step 4: Place credentials.json

Move the downloaded file to:
```
My_AI_Employee/credentials.json
```

**IMPORTANT**: This file is gitignored and will NOT be committed.

---

## Step 5: Run OAuth Setup Script

From the `My_AI_Employee` directory:

```bash
cd My_AI_Employee
uv run python setup_gmail_oauth_oob.py
```

**What happens**:
1. Script opens browser
2. You select your Gmail account
3. You grant permissions (read/send emails)
4. You copy the authorization code
5. You paste it into the terminal
6. Script creates `token.json`

**Expected output**:
```
Please visit this URL to authorize this application:
https://accounts.google.com/o/oauth2/auth?...

Enter the authorization code: [paste code here]

✅ Authentication successful!
✅ token.json created
```

---

## Step 6: Verify Setup

Check that both files exist:

```bash
ls -la My_AI_Employee/credentials.json
ls -la My_AI_Employee/token.json
```

Both should be present and gitignored.

---

## Step 7: Test Gmail Watcher

Start the Gmail watcher:

```bash
cd My_AI_Employee
uv run python watchers/gmail_watcher.py
```

**Expected output**:
```
INFO: Gmail watcher started
INFO: Checking for new emails every 60 seconds
INFO: Press Ctrl+C to stop
```

---

## Step 8: Send Test Email

1. From another email account (or the same Gmail account)
2. Send an email to your Gmail address
3. Subject: `Test Request: Please respond`
4. Body: `This is a test email for the AI Employee system.`

---

## Step 9: Verify Action Item Created

Check the Needs_Action folder:

```bash
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/
```

You should see a new file like:
```
EMAIL_20260117_180000_test_request.md
```

---

## Step 10: Process with Skill

In Claude Code, run:
```
/needs-action-triage
```

This will:
1. Read the action item
2. Create a plan in Plans/
3. Create an approval request in Pending_Approval/

---

## Step 11: Approve the Draft

1. Check Pending_Approval/ folder
2. Review the draft email
3. Edit if needed
4. Move to Approved/ folder:

```bash
mv My_AI_Employee/AI_Employee_Vault/Pending_Approval/APPROVAL_*.md \
   My_AI_Employee/AI_Employee_Vault/Approved/
```

---

## Step 12: Start Orchestrator

The orchestrator will execute the approved action:

```bash
cd My_AI_Employee
uv run python orchestrator.py
```

**Expected output**:
```
INFO: Orchestrator started
INFO: Watching Approved/ folder
INFO: Found approved action: APPROVAL_*.md
INFO: Executing email send via email_mcp
✅ Email sent successfully
INFO: Moved to Done/
```

---

## Step 13: Verify Email Sent

Check your Gmail inbox - you should have received the reply email!

---

## Troubleshooting

### Issue: "credentials.json not found"
**Solution**: Make sure you downloaded and placed credentials.json in My_AI_Employee/

### Issue: "Invalid grant" error
**Solution**: Delete token.json and re-run setup_gmail_oauth_oob.py

### Issue: "Gmail API not enabled"
**Solution**: Go to Google Cloud Console and enable Gmail API

### Issue: "Insufficient permissions"
**Solution**: Make sure you granted all requested permissions during OAuth flow

---

## What's Next?

After completing T093 (Gmail E2E test), you can:

1. **T094**: Verify Gmail acceptance scenarios (5 scenarios)
2. **T095-T096**: Test LinkedIn workflow (optional)
3. **T097-T098**: Test WhatsApp workflow (optional)
4. **T099-T101**: Test edge cases and verify requirements

Or skip to **Phase 10**: Documentation and polish

---

## Files Created

After successful setup:
- `My_AI_Employee/credentials.json` (gitignored)
- `My_AI_Employee/token.json` (gitignored)
- Action items in Needs_Action/
- Plans in Plans/
- Approval requests in Pending_Approval/
- Completed actions in Done/
- Audit logs in Logs/

---

**Ready to start? Follow Step 1 above!**

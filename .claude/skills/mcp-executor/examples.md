# MCP Executor Examples

## Email Backend Selection

All email examples work with both backends:

**Gmail API (Default)**: `EMAIL_BACKEND=gmail` in .env
- Secure OAuth 2.0
- Works with Gmail accounts
- Automatic token refresh

**SMTP (Universal)**: `EMAIL_BACKEND=smtp` in .env
- Works with ANY email provider
- TLS encryption
- Username/password authentication

The `send_email()` tool automatically selects the backend. No code changes needed - just change `.env`!

---

## Example 1: Execute Email Send (Gmail API)

### Approved Item in `/Approved/`

**File**: `email_client_update.md`

```markdown
---
type: action
source: approval_workflow
action_type: send_email
mcp_server: email
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T14:35:00Z
---

# Action: Send Email to Client

**To**: client@example.com
**Subject**: Project Update - Phase 1 Complete
**Body**:

Hi Sarah,

Great news! Phase 1 of the project is complete and ready for review.

Deliverables:
- Core API implementation
- Database schema
- Initial test suite

Next steps:
1. Review deliverables (by Jan 20)
2. Provide feedback (by Jan 25)
3. Start Phase 2 (Feb 3)

Please let me know if you have any questions.

Best regards,
[AI Employee]
```

### Executor Process

1. **Watches `/Approved/` folder** - Detects new email_client_update.md
2. **Reads action details** - Extracts recipient, subject, body
3. **Routes to email_mcp** - Calls email server
4. **Executes send_email()** - Sends via Gmail API
5. **Captures result**:
   ```
   ✅ SUCCESS
   Message ID: abc123xyz
   To: client@example.com
   Subject: Project Update - Phase 1 Complete
   Sent: 2026-01-14 14:36:00
   ```
6. **Moves to `/Done/`** - Files completed execution with result

### Result File in `/Done/`

**File**: `email_client_update_executed_20260114_143600.md`

```markdown
---
type: action
status: executed
action_type: send_email
mcp_server: email
approved_by: Jane Doe
executed_at: 2026-01-14T14:36:00Z
execution_time_seconds: 2.3
success: true
---

# Executed: Send Email to Client

## Original Action
To: client@example.com
Subject: Project Update - Phase 1 Complete

## Execution Result

✅ **SUCCESS**

**Message ID**: abc123xyz
**Sent At**: 2026-01-14 14:36:00 UTC
**Execution Time**: 2.3 seconds
**Status**: Email delivered to Gmail

## Audit Trail
- Created: 2026-01-14T14:30:00Z (by approval_workflow)
- Approved: 2026-01-14T14:35:00Z (by Jane Doe)
- Executed: 2026-01-14T14:36:00Z (by mcp_executor)

---
```

---

## Example 2: LinkedIn Post Creation

### Approved Item in `/Approved/`

**File**: `linkedin_automation_post.md`

```markdown
---
type: action
source: approval_workflow
action_type: create_post
mcp_server: linkedin
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T10:10:00Z
---

# Action: LinkedIn Post - Automation Insights

**Post Text**:

Just launched a new automation feature that helps clients save 5+ hours per week!

Building this taught us a lot. Here's what we learned:

1. Start with customer pain point (not cool tech)
2. Simple MVP wins over perfect features
3. Real feedback matters more than assumptions

If you're building automation, what's your #1 biggest challenge? Would love to hear.

**Hashtags**: #automation #productmanagement #startups
```

### Executor Process

1. **Detects post in `/Approved/`**
2. **Routes to linkedin_mcp server**
3. **Calls create_post()** with text and hashtags
4. **LinkedIn API response**:
   ```
   {
     "success": true,
     "post_id": "urn:li:share:7250000000000",
     "post_url": "https://linkedin.com/feed/update/urn:li:share:7250000000000",
     "published_at": "2026-01-14T10:15:00Z"
   }
   ```
5. **Moves to `/Done/` with result**

### Result File in `/Done/`

```markdown
---
type: action
status: executed
action_type: create_post
mcp_server: linkedin
executed_at: 2026-01-14T10:15:00Z
success: true
post_id: urn:li:share:7250000000000
post_url: https://linkedin.com/feed/update/urn:li:share:7250000000000
---

# Executed: LinkedIn Post

## Post Content

Just launched a new automation feature...

## Execution Result

✅ **SUCCESS - POST PUBLISHED**

**Post URL**: https://linkedin.com/feed/update/urn:li:share:7250000000000
**Published At**: 2026-01-14 10:15:00 UTC
**Status**: Live on LinkedIn

## Post Stats (Real-time)
- Views: [Will be updated by LinkedIn]
- Likes: [Will be updated by LinkedIn]
- Comments: [Will be updated by LinkedIn]

---
```

---

## Example 3: Browser Automation - Payment Form

### Approved Item in `/Approved/`

**File**: `payment_vendor_tech_solutions.md`

```markdown
---
type: action
source: approval_workflow
action_type: payment
mcp_server: browser
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T16:25:00Z
---

# Action: Payment Form Submission

**Vendor**: Tech Solutions Inc
**Amount**: $800 USD
**Invoice**: TS-2026-001

## Browser Automation Steps

### Step 1: Navigate to Payment Portal
- URL: https://techsolutions.example.com/payments

### Step 2: Fill Form Fields
- Selector: `input[name="invoice_number"]`
  Value: `TS-2026-001`

- Selector: `input[name="amount"]`
  Value: `800`

- Selector: `input[name="currency"]`
  Value: `USD`

### Step 3: Click Submit Button
- Selector: `button[type="submit"]`

### Step 4: Wait for Confirmation
- Wait for text: "Payment Received"
- Extract confirmation number from page

### Step 5: Screenshot Confirmation
- Take screenshot for audit trail
```

### Executor Process

1. **Reads form automation steps**
2. **Routes to playwright_mcp server**
3. **Executes steps in sequence**:
   ```
   Step 1: navigate_to("https://techsolutions.example.com/payments")
   Result: ✅ Page loaded

   Step 2a: fill_form("input[name='invoice_number']", "TS-2026-001")
   Result: ✅ Field filled

   Step 2b: fill_form("input[name='amount']", "800")
   Result: ✅ Field filled

   Step 2c: fill_form("input[name='currency']", "USD")
   Result: ✅ Field filled

   Step 3: click_button("button[type='submit']")
   Result: ✅ Button clicked

   Step 4: extract_text("div.confirmation")
   Result: ✅ Confirmation #: PAY-20260114-12345

   Step 5: Screenshot captured
   Result: ✅ Screenshot saved
   ```

4. **All steps succeeded** → Move to `/Done/` with confirmation details

### Result File in `/Done/`

```markdown
---
type: action
status: executed
action_type: payment
mcp_server: browser
executed_at: 2026-01-14T16:30:00Z
success: true
execution_time_seconds: 45.2
confirmation_number: PAY-20260114-12345
---

# Executed: Payment Form Submission

## Payment Details
- Vendor: Tech Solutions Inc
- Amount: $800 USD
- Invoice: TS-2026-001

## Execution Result

✅ **SUCCESS - PAYMENT PROCESSED**

**Confirmation Number**: PAY-20260114-12345
**Submitted At**: 2026-01-14 16:30:00 UTC
**Status**: Payment Received

## Execution Timeline
1. Navigate to portal: 2.1s
2. Fill form fields: 3.2s
3. Submit form: 1.5s
4. Wait for confirmation: 38.2s (page processing)
5. Extract confirmation: 0.2s

**Total Time**: 45.2 seconds

## Confirmation Screenshot
[Screenshot URL: /Done/attachments/payment_confirmation_20260114.png]

---
```

---

## Example 4: Execution Failure - Auto-Retry

### Failed Execution Item

**File**: `email_client_payment_failed_retry1.md`

```markdown
---
type: action
status: failed
action_type: send_email
mcp_server: email
executed_at: 2026-01-14T14:36:00Z
execution_time_seconds: 0.5
error: "Gmail API error: 401 Unauthorized - Token expired"
retry_count: 1
next_retry: 2026-01-14T15:00:00Z
---

# FAILED: Send Email - Retry 1 of 3

## Original Action
To: accounting@vendor.com
Subject: Invoice Payment Confirmation
Body: [email content]

## Execution Attempt 1

❌ **FAILED**

**Error**: Gmail API error: 401 Unauthorized - Token expired
**Time**: 2026-01-14 14:36:00
**Attempt**: 1/3

## Retry Schedule

- Retry 1: 2026-01-14 14:36:00 (COMPLETED - FAILED)
- Retry 2: 2026-01-14 15:00:00 (PENDING - 24 minutes)
- Retry 3: 2026-01-14 17:00:00 (PENDING - 2 hours 24 minutes)
- After retry 3: Manual review required

## Notes

Token expiration detected. Executor will automatically refresh token and retry.
If retries continue to fail, may need to re-authenticate Gmail OAuth flow.

---
```

### After Token Refresh - Retry Succeeds

**File**: `email_client_payment_executed_retry2.md`

```markdown
---
type: action
status: executed
action_type: send_email
mcp_server: email
original_attempt: 2026-01-14T14:36:00Z
executed_at: 2026-01-14T15:02:00Z
execution_time_seconds: 1.8
retry_count: 2
success: true
---

# Executed: Send Email (Retry 2)

## Original Action
To: accounting@vendor.com
Subject: Invoice Payment Confirmation
Body: [email content]

## Retry Timeline

**Attempt 1**: 2026-01-14 14:36:00
- Result: ❌ FAILED (token expired)
- Wait: 25 minutes

**Attempt 2**: 2026-01-14 15:01:00
- Token refresh: Successful
- Result: ✅ SUCCESS
- Message ID: xyz789abc

## Final Status

✅ **SUCCESS - EMAIL SENT**

**Sent At**: 2026-01-14 15:01:00 UTC
**Attempts**: 2 (1 failure + 1 success)
**Total Time**: 25 minutes 1 second
**Status**: Email delivered to accounting@vendor.com

---
```

---

## Example 5: Multiple Actions in Sequence

### Three Approved Items

When multiple items exist in `/Approved/`:

```
/Approved/
├── step1_notify_client_email.md
├── step2_post_linkedin_update.md
└── step3_create_calendar_event.md
```

### Executor Processes All

```
Checking /Approved/ folder...
Found 3 items

Processing: step1_notify_client_email.md
  → email_mcp: send_email() ✅ SUCCESS
  → Moved to /Done/

Processing: step2_post_linkedin_update.md
  → linkedin_mcp: create_post() ✅ SUCCESS
  → Moved to /Done/

Processing: step3_create_calendar_event.md
  → browser_mcp: navigate + fill + click ✅ SUCCESS
  → Moved to /Done/

Summary: 3/3 actions executed successfully
Execution time: 52.3 seconds
```

All results available in `/Done/` folder with full audit trail.

---

## Executor Status Dashboard

```bash
python scripts/executor_status.py
```

**Output**:

```
╔════════════════════════════════════════╗
║    MCP EXECUTOR STATUS DASHBOARD       ║
╚════════════════════════════════════════╝

Uptime: 12h 34m 22s
Status: ✅ ONLINE

PENDING EXECUTION
├─ email_client_update.md (1 item)
├─ linkedin_automation_post.md (1 item)
└─ payment_vendor_tech_solutions.md (1 item)

EXECUTED (Today)
├─ ✅ 12 successful
├─ ❌ 1 failed (retry pending)
├─ 🔄 1 retrying

STATISTICS
├─ Success Rate: 92.3%
├─ Avg Execution Time: 8.4s
├─ Total Items Processed: 178
└─ Total Execution Time: 24h 31m

MCP SERVERS HEALTH
├─ email-mcp: ✅ ONLINE (1523 executions)
├─ linkedin-mcp: ✅ ONLINE (234 executions)
├─ playwright-mcp: ✅ ONLINE (89 executions)
└─ Overall: ✅ HEALTHY

NEXT ACTIONS
├─ Process pending in 5 seconds
├─ Retry failed in 18 seconds
└─ Check MCP servers health in 30 seconds
```

---

## Example 6: Email Send via SMTP Backend

### Setup Configuration

**File**: `.env`

```bash
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@company.com
SMTP_PASSWORD=company-app-password
SMTP_FROM_ADDRESS=notifications@company.com
```

### Approved Item in `/Approved/`

**File**: `email_outlook_send.md`

```markdown
---
type: action
source: approval_workflow
action_type: send_email
mcp_server: email
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T09:30:00Z
---

# Action: Send Email via SMTP (Outlook)

**To**: manager@clientcompany.com
**CC**: stakeholder@clientcompany.com
**Subject**: Quarterly Review - Q1 2026 Results
**Body**:

Hi Team,

Please find attached our Q1 2026 review with the following highlights:

• Revenue growth: 23% YoY
• New clients acquired: 12
• Market share: 5.2%

Key metrics and detailed analysis are in the attached document.

Let me know if you have any questions.

Best regards,
[AI Employee]
```

### Executor Process

1. **Watches `/Approved/` folder** - Detects email_outlook_send.md
2. **Reads email details** - Extracts to, cc, subject, body
3. **Routes to email_mcp** - Calls email server
4. **Backend selection** - EMAIL_BACKEND=smtp → Uses SMTPBackend
5. **SMTP Connection**:
   ```
   Connect to: smtp.office365.com:587
   StartTLS: Encryption enabled
   Login: user@company.com / ****
   From: notifications@company.com
   ```
6. **Sends email**:
   ```
   To: manager@clientcompany.com
   CC: stakeholder@clientcompany.com
   Subject: Quarterly Review - Q1 2026 Results
   Body: [Full email content]
   ```
7. **Returns success**:
   ```json
   {
     "success": true,
     "message_id": "smtp-2026-01-14T09:35:00Z",
     "timestamp": "2026-01-14T09:35:00Z",
     "backend_used": "smtp"
   }
   ```
8. **Moves to `/Done/`** - Files completed execution with result

### Result File in `/Done/`

**File**: `email_outlook_send_executed_20260114_093500.md`

```markdown
---
type: action
status: executed
action_type: send_email
mcp_server: email
approved_by: Jane Doe
executed_at: 2026-01-14T09:35:00Z
execution_time_seconds: 1.8
success: true
backend_used: smtp
---

# Executed: Send Email via SMTP (Outlook)

## Original Action
To: manager@clientcompany.com
CC: stakeholder@clientcompany.com
Subject: Quarterly Review - Q1 2026 Results

## Execution Result

✅ **SUCCESS - EMAIL SENT VIA SMTP**

**Message ID**: smtp-2026-01-14T09:35:00Z
**Sent At**: 2026-01-14 09:35:00 UTC
**Execution Time**: 1.8 seconds
**Backend Used**: SMTP (Outlook - Office 365)
**From**: notifications@company.com

## Recipients
- To: manager@clientcompany.com
- CC: stakeholder@clientcompany.com
- Status: Delivered

## Audit Trail
- Created: 2026-01-14T09:30:00Z (by approval_workflow)
- Approved: 2026-01-14T09:32:00Z (by Jane Doe)
- Executed: 2026-01-14T09:35:00Z (by mcp_executor via SMTP)

---
```

---

## Example 7: SMTP Backend - Custom Email Provider

### Setup Configuration

**File**: `.env`

```bash
EMAIL_BACKEND=smtp
SMTP_HOST=mail.company.com
SMTP_PORT=587
SMTP_USERNAME=notifications@company.com
SMTP_PASSWORD=secure-password-123
SMTP_FROM_ADDRESS=noreply@company.com
```

### Email Action

```markdown
---
type: action
action_type: send_email
status: approved
approved_by: Admin
---

# Action: Send Notification via Custom SMTP

**To**: customer@example.com
**BCC**: admin@company.com
**Subject**: Your Account Has Been Updated
**Body**:

Your account settings have been updated successfully.

If you did not make these changes, please contact us immediately.

Changes made:
- Email address verified
- Two-factor authentication enabled
- Security settings updated

For support: support@company.com
```

### Execution

**Backend**: Custom SMTP (mail.company.com:587)
**Result**: ✅ SUCCESS (2.1s execution time)

---

## Example 8: Switching Between Backends

### Scenario: User wants to switch from Gmail to Outlook

**Before** (Gmail API):
```bash
# .env
EMAIL_BACKEND=gmail
GMAIL_TOKEN_FILE=token.json
GMAIL_CREDENTIALS_FILE=credentials.json
```

**After** (Outlook SMTP):
```bash
# .env
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@company.com
SMTP_PASSWORD=app-password-here
```

**Code Changes Required**: ❌ NONE!

The `send_email()` tool automatically adapts. Just:
1. Change `EMAIL_BACKEND` in .env
2. Set appropriate credentials
3. Restart executor (will auto-detect new backend)
4. Next email uses new backend

All existing `/Approved/` items work unchanged!

---

## Email Configuration Comparison

| Scenario | Backend | Configuration | Setup Time |
|----------|---------|----------------|-----------|
| **Gmail (Personal)** | Gmail API | OAuth 2.0 credentials | ~5 min |
| **Gmail (Business)** | SMTP | App password | ~2 min |
| **Outlook 365** | SMTP | Office 365 credentials | ~2 min |
| **Yahoo Mail** | SMTP | App password | ~2 min |
| **Custom Server** | SMTP | Server details + credentials | ~5 min |

**Recommendation**: Start with Gmail API (most secure). Switch to SMTP if you need multi-provider support.

---

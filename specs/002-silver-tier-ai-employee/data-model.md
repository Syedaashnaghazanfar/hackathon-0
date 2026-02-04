# Data Model: Silver Tier Entities

**Feature**: Silver Tier AI Employee
**Date**: 2026-01-22
**Phase**: 1 (Design)

This document defines the data schemas for all entities in the Silver tier system. All entities are stored as markdown files with YAML frontmatter in the Obsidian vault.

---

## 1. Action Item

**Storage Location**: `/Needs_Action/*.md`
**Purpose**: Represents an incoming request or notification requiring attention from any watcher (Gmail, WhatsApp, LinkedIn, filesystem).

### YAML Frontmatter Schema

```yaml
# Bronze Tier Fields (Preserved)
type: email | whatsapp | linkedin | file_drop
received: 2026-01-22T10:30:00Z  # ISO 8601 timestamp
status: pending | processed
priority: high | medium | low | auto
source_id: gmail_abc123def4567890  # Unique hash for duplicate detection

# Silver Tier Additions
sender: user@example.com | +1234567890 | LinkedIn Connection Name
subject: Email subject line | First 50 chars of message | Notification title
tags: [invoice, urgent, payment]  # Optional classification tags
action_required: true | false  # Does this need immediate attention?
deadline: 2026-01-23T17:00:00Z  # Optional deadline from content analysis
```

### Markdown Body Structure

```markdown
## Summary
[Brief 1-2 sentence description of what needs action]

## Details
[Full context extracted from source]
- **From**: [sender]
- **Received**: [timestamp]
- **Channel**: [Gmail/WhatsApp/LinkedIn/File]
- **Content**: [extracted message/email body/file content]

## Suggested Actions
- [ ] [Action 1 - e.g., Reply to email]
- [ ] [Action 2 - e.g., Schedule meeting]
- [ ] [Action 3 - e.g., Update dashboard]
```

### Python Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional

@dataclass
class ActionItemSchema:
    """Represents an action item from any watcher source."""

    # Bronze tier fields
    type: Literal["email", "whatsapp", "linkedin", "file_drop"]
    received: datetime
    status: Literal["pending", "processed"]
    priority: Literal["high", "medium", "low", "auto"]
    source_id: str

    # Silver tier additions
    sender: str
    subject: str
    tags: List[str] = field(default_factory=list)
    action_required: bool = True
    deadline: Optional[datetime] = None

    # Metadata (not in frontmatter, derived from body)
    summary: str = ""
    details: str = ""
    suggested_actions: List[str] = field(default_factory=list)

    def to_frontmatter_dict(self) -> dict:
        """Convert to YAML frontmatter dict."""
        return {
            "type": self.type,
            "received": self.received.isoformat(),
            "status": self.status,
            "priority": self.priority,
            "source_id": self.source_id,
            "sender": self.sender,
            "subject": self.subject,
            "tags": self.tags,
            "action_required": self.action_required,
            "deadline": self.deadline.isoformat() if self.deadline else None
        }
```

### Validation Rules

- `source_id` MUST be unique across all action items (enforced by deduplication)
- `received` timestamp MUST be in UTC timezone
- `type` determines which watcher created the item
- `priority` is automatically classified:
  - **high**: Contains urgent keywords OR action_required=true + deadline < 24 hours
  - **medium**: Standard business communications
  - **low**: Newsletters, automated notifications
  - **auto**: Internal vault operations (e.g., scheduled dashboard update)

### State Transitions

```
pending → processed (after triage creates Plan.md)
```

### Example

```yaml
---
type: email
received: 2026-01-22T14:30:00Z
status: pending
priority: high
source_id: gmail_f8e3d2c1a0b9
sender: boss@company.com
subject: Q4 Report - Need by EOD
tags: [urgent, report, deadline]
action_required: true
deadline: 2026-01-22T17:00:00Z
---

## Summary
Boss requesting Q4 financial report by end of day today.

## Details
- **From**: boss@company.com
- **Received**: 2026-01-22 14:30 UTC
- **Channel**: Gmail
- **Content**:
  > Hi, can you send me the Q4 report by 5pm today? We have the board meeting tomorrow morning.
  > Thanks!

## Suggested Actions
- [ ] Pull Q4 data from spreadsheet
- [ ] Generate PDF report
- [ ] Reply with attached report
```

---

## 2. Execution Plan

**Storage Location**: `/Plans/*.md`
**Purpose**: Represents the AI's proposed execution strategy for an action item.

### YAML Frontmatter Schema

```yaml
created: 2026-01-22T14:35:00Z
status: pending_approval | approved | rejected | completed
classification: auto-approve | require-approval
original_item: 2026-01-22_urgent_quarterly_report.md  # Link to source action item
estimated_duration: 15 minutes  # Optional
mcp_servers_required: [email-server]  # List of MCP servers needed
```

### Markdown Body Structure

```markdown
## Objective
[What this plan aims to accomplish]

## Classification
**Type**: auto-approve | require-approval
**Rationale**: [Why this classification was chosen based on Company_Handbook.md rules]

## Execution Steps
1. **[Step 1 Name]**
   - Tool: [MCP server name].[tool name]
   - Parameters: [brief description]
   - Expected outcome: [what happens]

2. **[Step 2 Name]**
   - ...

## Approval Requirements
[If require-approval: risk assessment details]
[If auto-approve: justification for automatic execution]

## Rollback Plan
[If something goes wrong, how to undo or mitigate]
```

### Python Dataclass

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Optional

@dataclass
class ExecutionPlanSchema:
    """Represents an AI-generated execution plan."""

    created: datetime
    status: Literal["pending_approval", "approved", "rejected", "completed"]
    classification: Literal["auto-approve", "require-approval"]
    original_item: str
    estimated_duration: Optional[str] = None
    mcp_servers_required: List[str] = field(default_factory=list)

    # Body content
    objective: str = ""
    classification_rationale: str = ""
    execution_steps: List[str] = field(default_factory=list)
    approval_requirements: str = ""
    rollback_plan: str = ""
```

### Validation Rules

- `classification` MUST be either `auto-approve` or `require-approval`
- `require-approval` plans MUST include risk assessment
- `auto-approve` plans MUST reference Company_Handbook.md rule justifying automation
- `mcp_servers_required` MUST list all MCP servers used in execution steps

### State Transitions

```
pending_approval → approved (human moves to /Approved/)
pending_approval → rejected (human moves to /Rejected/)
approved → completed (mcp-executor successfully executes)
```

---

## 3. Approval Request

**Storage Location**: `/Pending_Approval/*.md`
**Purpose**: Requests human approval for a sensitive external action.

### YAML Frontmatter Schema

```yaml
type: approval_request
action_type: send_email | post_linkedin | browser_automation | api_call
created: 2026-01-22T14:40:00Z
deadline: 2026-01-23T17:00:00Z  # Optional expiration
priority: high | medium | low
requires_approval: true
original_item: 2026-01-22_urgent_quarterly_report.md
mcp_server: email-server
tool_name: send_email
approval_status: pending | approved | rejected
approved_by: null  # Set when moved to /Approved/
approved_at: null  # Timestamp of approval
rejection_reason: null  # Set when moved to /Rejected/
```

### Markdown Body Structure

```markdown
## Proposed Action
[Clear description of what will be executed]

## Justification
[Why this action is necessary, context from original request]

## Risk Assessment
- **Impact**: [financial | reputational | operational]
  - [Detailed impact analysis]
- **Reversibility**: [can this be undone if something goes wrong?]
  - [Explanation of undo process or irreversibility]
- **Blast Radius**: [who/what is affected?]
  - [List of affected parties, systems, or data]

## Execution Details
**MCP Server**: email-server
**Tool**: send_email
**Parameters**:
```json
{
  "to": "boss@company.com",
  "subject": "Q4 2025 Financial Report",
  "body": "[Preview of email content...]",
  "attachments": ["Q4_Report_2025.pdf"]
}
```

## Approval Decision
**[ ] APPROVE** - Move this file to `/Approved/` folder to execute
**[ ] REJECT** - Move this file to `/Rejected/` folder and add `rejection_reason` to frontmatter

---
**Note**: This action CANNOT be undone after execution. Review carefully before approving.
```

### Python Dataclass

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Literal, Optional

@dataclass
class ApprovalRequestSchema:
    """Represents a human approval request."""

    type: Literal["approval_request"] = "approval_request"
    action_type: Literal["send_email", "post_linkedin", "browser_automation", "api_call"]
    created: datetime
    deadline: Optional[datetime]
    priority: Literal["high", "medium", "low"]
    requires_approval: bool = True
    original_item: str
    mcp_server: str
    tool_name: str
    approval_status: Literal["pending", "approved", "rejected"] = "pending"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # Body content
    proposed_action: str = ""
    justification: str = ""
    risk_impact: str = ""
    risk_reversibility: str = ""
    risk_blast_radius: str = ""
    tool_parameters: Dict[str, Any] = field(default_factory=dict)
```

### Validation Rules

- `action_type` MUST match actual MCP tool being called
- `mcp_server` and `tool_name` MUST be valid registered MCP server/tool combinations
- `tool_parameters` MUST have all sensitive data already sanitized for display
- `deadline` if present triggers auto-rejection if passed without approval

### State Transitions

```
pending → approved (human moves file to /Approved/)
pending → rejected (human moves file to /Rejected/ with rejection_reason)
approved → executed (mcp-executor processes)
pending → rejected (deadline expired, auto-rejected by approval-workflow-manager)
```

---

## 4. Audit Log Entry

**Storage Location**: `/Logs/YYYY-MM-DD.json`
**Purpose**: Records every external action execution for compliance and debugging.

### JSON Schema

```json
{
  "timestamp": "2026-01-22T15:00:00Z",
  "action_id": "2026-01-22_urgent_quarterly_report",
  "action_type": "send_email",
  "user": "human-approver",
  "ai_agent": "claude-code-sonnet-4.5",
  "approval_reason": "Q4 board meeting deadline",
  "execution_status": "success",
  "mcp_server": "email-server",
  "tool_name": "send_email",
  "tool_inputs_sanitized": {
    "to": "boss@company.com",
    "subject": "Q4 2025 Financial Report",
    "body_preview": "Please find attached the Q4 financial...",
    "attachments": ["Q4_Report_2025.pdf"]
  },
  "tool_output_sanitized": {
    "message_id": "msg_abc123",
    "status": "sent",
    "sent_at": "2026-01-22T15:00:05Z"
  },
  "error": null,
  "retry_count": 0,
  "execution_duration_ms": 1234
}
```

### Python Dataclass

```python
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Literal, Optional
import json

@dataclass
class AuditLogEntry:
    """Represents a single audit log entry."""

    timestamp: datetime
    action_id: str
    action_type: Literal["send_email", "post_linkedin", "browser_automation", "api_call"]
    user: str
    ai_agent: str
    approval_reason: str
    execution_status: Literal["success", "failure", "pending"]
    mcp_server: str
    tool_name: str
    tool_inputs_sanitized: Dict[str, Any]
    tool_output_sanitized: Dict[str, Any]
    error: Optional[str] = None
    retry_count: int = 0
    execution_duration_ms: Optional[int] = None

    def to_json(self) -> str:
        """Convert to JSON string for logging."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "AuditLogEntry":
        """Load from JSON string."""
        data = json.loads(json_str)
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
```

### Validation Rules

- `timestamp` MUST be in UTC timezone
- `tool_inputs_sanitized` and `tool_output_sanitized` MUST have ALL credentials redacted
- `execution_status` = `"failure"` requires non-null `error` field
- `retry_count` tracks number of retry attempts (0 = first attempt succeeded)

### Sanitization Requirements

Before logging, the following MUST be redacted:
- API keys → `<REDACTED_API_KEY>`
- OAuth tokens → `<REDACTED_OAUTH_TOKEN>`
- Passwords → `<REDACTED_PASSWORD>`
- Credit card numbers → `<REDACTED_CC_LAST4:1234>`
- Full email addresses in PII context → `a****@example.com` (preserve domain for debugging)

---

## 5. Watcher Process State

**Storage Location**: `.{watcher_name}_dedupe.json` (in project root, gitignored)
**Purpose**: Tracks processed message IDs to prevent duplicate action item creation.

### JSON Schema

```json
{
  "watcher_name": "gmail",
  "last_updated": "2026-01-22T15:00:00Z",
  "processed_ids": [
    "gmail_f8e3d2c1a0b9",
    "gmail_abc123def4567",
    "gmail_xyz789ghi012"
  ],
  "total_processed": 3,
  "uptime_start": "2026-01-22T08:00:00Z"
}
```

### Python Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal
import json

@dataclass
class WatcherState:
    """Tracks watcher deduplication state."""

    watcher_name: Literal["gmail", "whatsapp", "linkedin", "filesystem"]
    last_updated: datetime
    processed_ids: List[str] = field(default_factory=list)
    total_processed: int = 0
    uptime_start: datetime = field(default_factory=datetime.utcnow)

    def has_processed(self, source_id: str) -> bool:
        """Check if source_id already processed."""
        return source_id in self.processed_ids

    def mark_processed(self, source_id: str) -> None:
        """Add source_id to processed set."""
        if source_id not in self.processed_ids:
            self.processed_ids.append(source_id)
            self.total_processed += 1
            self.last_updated = datetime.utcnow()

    def save(self, filepath: str) -> None:
        """Save state to JSON file."""
        data = {
            "watcher_name": self.watcher_name,
            "last_updated": self.last_updated.isoformat(),
            "processed_ids": self.processed_ids,
            "total_processed": self.total_processed,
            "uptime_start": self.uptime_start.isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "WatcherState":
        """Load state from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        data["uptime_start"] = datetime.fromisoformat(data["uptime_start"])
        return cls(**data)
```

### Rotation Strategy

- Keep last 1000 processed IDs (rolling window)
- Rotate deduplication file monthly (archive old state)
- Handle race conditions: use atomic file writes (write to temp, then move)

---

## 6. MCP Server Configuration

**Storage Location**: `.env` (gitignored)
**Purpose**: Stores credentials and configuration for MCP servers.

### Environment Variables Schema

```bash
# Gmail MCP Server
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify

# LinkedIn MCP Server
LINKEDIN_ACCESS_TOKEN=<oauth2_access_token>
LINKEDIN_PERSON_URN=urn:li:person:ABC123

# Browser MCP Server (WhatsApp)
WHATSAPP_SESSION_DIR=.whatsapp_session
WHATSAPP_CDP_PORT=9222

# Global Settings
DRY_RUN=false
LOG_LEVEL=INFO
VAULT_ROOT=AI_Employee_Vault
```

### Python Config Dataclass

```python
from dataclasses import dataclass
from dotenv import load_dotenv
import os

@dataclass
class Config:
    """Centralized configuration from .env file."""

    # Vault
    vault_root: str

    # Gmail
    gmail_credentials_file: str
    gmail_token_file: str
    gmail_scopes: str

    # LinkedIn
    linkedin_access_token: str
    linkedin_person_urn: str

    # WhatsApp
    whatsapp_session_dir: str
    whatsapp_cdp_port: int

    # Global
    dry_run: bool
    log_level: str

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from .env file."""
        load_dotenv()
        return cls(
            vault_root=os.getenv("VAULT_ROOT", "AI_Employee_Vault"),
            gmail_credentials_file=os.getenv("GMAIL_CREDENTIALS_FILE"),
            gmail_token_file=os.getenv("GMAIL_TOKEN_FILE"),
            gmail_scopes=os.getenv("GMAIL_SCOPES", "https://www.googleapis.com/auth/gmail.modify"),
            linkedin_access_token=os.getenv("LINKEDIN_ACCESS_TOKEN"),
            linkedin_person_urn=os.getenv("LINKEDIN_PERSON_URN"),
            whatsapp_session_dir=os.getenv("WHATSAPP_SESSION_DIR", ".whatsapp_session"),
            whatsapp_cdp_port=int(os.getenv("WHATSAPP_CDP_PORT", "9222")),
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )

    def validate(self) -> None:
        """Validate required credentials are present."""
        if not self.gmail_credentials_file:
            raise ValueError("GMAIL_CREDENTIALS_FILE not set in .env")
        # ... additional validations
```

---

## Entity Relationships

```
Action Item (Needs_Action/)
    ↓
Execution Plan (Plans/)
    ↓
Approval Request (Pending_Approval/)
    ↓ (human moves file)
Approved Action (Approved/)
    ↓
Audit Log Entry (Logs/YYYY-MM-DD.json)
    ↓
Completed Action (Done/) OR Failed Action (Failed/)
```

## Storage Summary

| Entity | Format | Location | Gitignored? |
|--------|--------|----------|-------------|
| Action Item | Markdown + YAML | /Needs_Action/ | Yes (vault) |
| Execution Plan | Markdown + YAML | /Plans/ | Yes (vault) |
| Approval Request | Markdown + YAML | /Pending_Approval/ | Yes (vault) |
| Audit Log Entry | JSON (daily) | /Logs/YYYY-MM-DD.json | Yes (vault) |
| Watcher State | JSON | .{watcher}_dedupe.json | Yes (project root) |
| MCP Config | .env | .env | Yes (project root) |

---

## Next Steps

- Create MCP server contracts (OpenAPI specs for email, LinkedIn, browser tools)
- Create quickstart.md (setup guide for credentials, vault initialization)
- Update agent context with new entity schemas


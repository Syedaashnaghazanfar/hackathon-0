# Feature Specification: Silver Tier AI Employee

**Feature Branch**: `002-silver-ai-employee`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "Build a Silver Tier Personal AI Employee — a functional assistant that monitors multiple communication channels, reasons about what actions to take, and executes approved actions on my behalf."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Client Email Response (Priority: P1)

A client emails asking for a project update. The AI Employee detects the email, creates a plan for responding, drafts the response, requests my approval, and sends the email once I approve.

**Why this priority**: This is the most common and high-value use case. Responding to clients quickly maintains business relationships and demonstrates professionalism. This single capability alone provides immediate value.

**Independent Test**: Can be fully tested by sending a test email to the monitored inbox, verifying that an action item is created, a plan is generated, an approval request appears, and the email is sent after approval.

**Acceptance Scenarios**:

1. **Given** the AI Employee is monitoring my Gmail inbox, **When** a client sends an email asking for a project update, **Then** an action item appears in my vault's Needs_Action folder within 2 minutes with the email content and sender information.

2. **Given** an action item exists for a client email, **When** the AI Employee processes it, **Then** a Plan.md file is created explaining the recommended response based on my Company_Handbook.md rules.

3. **Given** a plan recommends sending an email response, **When** the AI Employee creates the draft, **Then** an approval request appears in my Pending_Approval folder with the complete draft email for my review.

4. **Given** an approval request exists for an email, **When** I move the file to the Approved folder, **Then** the email is sent within 10 seconds and a completion record appears in the Done folder with send confirmation.

5. **Given** an approval request exists for an email, **When** I move the file to the Rejected folder, **Then** no email is sent and the rejection is logged with my reason.

---

### User Story 2 - LinkedIn Business Post (Priority: P2)

The AI Employee proactively creates LinkedIn posts about my business to generate sales leads. It drafts posts based on my business activities and schedule, requests approval, and publishes once I approve.

**Why this priority**: Proactive business development and lead generation. While less urgent than client responses, this provides ongoing value by maintaining business visibility and attracting potential clients without requiring me to remember to post.

**Independent Test**: Can be tested by triggering a scheduled post time, verifying the draft post is created with relevant business content, approving it, and confirming it publishes to LinkedIn with the correct content.

**Acceptance Scenarios**:

1. **Given** my Company_Handbook.md specifies posting on Mondays and Thursdays, **When** the scheduled time arrives, **Then** the AI Employee creates a draft LinkedIn post based on recent business activities from my vault.

2. **Given** a draft LinkedIn post is created, **When** the AI Employee prepares it for approval, **Then** an approval request appears in Pending_Approval with the complete post text and any hashtags.

3. **Given** I approve a LinkedIn post, **When** the AI Employee publishes it, **Then** the post appears on my LinkedIn profile and a completion record in Done includes the post URL and initial engagement metrics.

4. **Given** I reject a LinkedIn post draft, **When** I provide feedback in the rejection, **Then** the AI Employee can incorporate that feedback into future post drafts.

---

### User Story 3 - WhatsApp Client Message (Priority: P3)

A client sends an urgent WhatsApp message asking for help. The AI Employee detects the message, creates a plan, drafts a reply, requests approval, and sends the response once I approve.

**Why this priority**: Important for client communication but less frequent than email. WhatsApp is often used for urgent matters, so having automated detection and response preparation is valuable, though it happens less often than email communication.

**Independent Test**: Can be tested by sending a test WhatsApp message containing urgent keywords, verifying detection, plan creation, approval request, and message sending after approval.

**Acceptance Scenarios**:

1. **Given** the AI Employee is monitoring WhatsApp Web, **When** a message arrives containing keywords like "urgent", "help", "asap", "invoice", or "payment", **Then** an action item is created in Needs_Action within 2 minutes.

2. **Given** a WhatsApp message action item exists, **When** the AI Employee processes it, **Then** a plan is created with a recommended response based on the message content and my Company_Handbook.md rules.

3. **Given** a plan recommends sending a WhatsApp reply, **When** the AI Employee creates the draft, **Then** an approval request appears with the complete message text for my review.

4. **Given** I approve a WhatsApp response, **When** the AI Employee sends it, **Then** the message is delivered and a completion record appears in Done with delivery confirmation.

---

### Edge Cases

- **What happens when Gmail API is down?** The system queues outgoing emails locally and retries sending when the API becomes available again. No emails are lost, and I'm notified of the queue status.

- **What happens when I don't approve an action for 24 hours?** The approval request expires and I receive a notification. The action is moved to a separate "Expired" status and I can manually re-activate it if still relevant.

- **What happens when WhatsApp session expires?** The system detects the expired session, stops the WhatsApp watcher, and notifies me to re-scan the QR code. Other watchers continue operating normally.

- **What happens when two watchers create duplicate action items?** The system detects duplicates by comparing content and timestamps, merges them into a single action item, and notes both sources in the metadata.

- **What happens when I reject an action?** The rejection is logged with my reason (if provided), the action is moved to Rejected folder, and the system does not retry or recreate similar actions without new input.

- **What happens when an action fails during execution?** The system retries up to 3 times with exponential backoff (immediate, 25 seconds, 2 hours). After 3 failures, the action moves to Failed folder with complete error details for my review.

- **What happens when LinkedIn rate limits are hit?** The system queues pending posts, respects the rate limit timing, and automatically publishes when the limit resets. I'm notified of the delay.

- **What happens when my vault is locked or inaccessible?** The system writes to a temporary buffer location and syncs all pending items to the vault once it becomes accessible again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST continuously monitor Gmail inbox for new emails and create action items for messages from known contacts or containing important keywords.

- **FR-002**: System MUST continuously monitor WhatsApp messages for new messages containing urgent keywords ("urgent", "help", "asap", "invoice", "payment").

- **FR-003**: System MUST continuously monitor LinkedIn for new notifications, connection requests, and messages.

- **FR-004**: System MUST read Company_Handbook.md to understand my rules, preferences, and decision-making criteria when processing action items.

- **FR-005**: System MUST create detailed Plan.md files for each action item explaining what should be done and why, based on Company_Handbook.md rules.

- **FR-006**: System MUST create approval requests in the Pending_Approval folder for all external actions (sending emails, posting to LinkedIn, sending WhatsApp messages, making payments).

- **FR-007**: System MUST NOT execute any external action until I explicitly approve it by moving the approval request to the Approved folder.

- **FR-008**: System MUST execute approved actions within 10 seconds of approval for time-sensitive communications.

- **FR-009**: System MUST log all executed actions with complete audit trail including timestamp, action type, who approved, and execution result.

- **FR-010**: System MUST move completed actions to the Done folder with execution results and confirmation details.

- **FR-011**: System MUST move failed actions to the Failed folder with error details and retry history.

- **FR-012**: System MUST support rejection of actions by moving approval requests to the Rejected folder, and must not retry rejected actions.

- **FR-013**: System MUST generate LinkedIn posts on a schedule defined in Company_Handbook.md using recent business activities from the vault as content.

- **FR-014**: System MUST update Dashboard.md with current status including pending actions, recent completions, and system health.

- **FR-015**: System MUST retry failed actions up to 3 times with exponential backoff before marking as permanently failed.

- **FR-016**: System MUST continue operating when one watcher fails, with other watchers functioning normally (graceful degradation).

- **FR-017**: System MUST detect and merge duplicate action items created by multiple watchers for the same event.

- **FR-018**: System MUST expire approval requests that remain unapproved for 24 hours and notify me of expiration.

- **FR-019**: System MUST queue actions locally when external services are unavailable and process the queue when services are restored.

- **FR-020**: System MUST notify me when critical errors occur (authentication failures, watcher crashes, vault inaccessibility).

### Key Entities

- **Action Item**: Represents something that needs attention, created by watchers when they detect important events. Contains source information (email, WhatsApp, LinkedIn), content, priority, and status. Lives in Needs_Action folder until processed.

- **Plan**: Detailed explanation of what should be done for an action item and why. Created by analyzing the action item against Company_Handbook.md rules. Contains recommended actions, reasoning, and next steps.

- **Approval Request**: Request for human approval before executing an external action. Contains the complete proposed action (draft email, post content, etc.), justification, and approval/rejection status. Lives in Pending_Approval until moved to Approved or Rejected.

- **Execution Record**: Record of a completed action. Contains what was done, when, who approved it, execution result, and any relevant confirmation details (email sent confirmation, post URL, etc.). Lives in Done or Failed folder.

- **Audit Log**: Comprehensive log entry for every external action. Contains timestamp, action type, actor, target, approval status, approver name, and execution result. Used for compliance and troubleshooting.

- **Company Handbook**: My rules, preferences, and decision-making criteria. Defines how the AI Employee should behave, what requires approval, communication tone, scheduling preferences, and business policies.

- **Dashboard**: Real-time summary of system status. Shows pending actions, recent completions, watcher health, and any issues requiring attention.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System monitors Gmail, WhatsApp, and LinkedIn continuously (24/7) without requiring manual intervention or restarts.

- **SC-002**: 100% of external actions go through approval workflow - zero actions are executed without explicit human approval.

- **SC-003**: I can approve or reject any action in under 30 seconds by simply moving a file between folders in my vault.

- **SC-004**: All executed actions have a complete audit trail showing who approved, when, what was done, and the result.

- **SC-005**: Approved email responses are sent within 10 seconds of approval, ensuring timely client communication.

- **SC-006**: Scheduled LinkedIn posts are created and published on time, generating measurable engagement (likes, comments, shares).

- **SC-007**: When one watcher fails, the other watchers continue operating normally, ensuring the system remains functional (graceful degradation).

- **SC-008**: Action items appear in my vault within 2 minutes of the triggering event (email received, WhatsApp message, LinkedIn notification).

- **SC-009**: Failed actions are retried automatically up to 3 times before requiring manual intervention, reducing the number of actions I need to handle manually.

- **SC-010**: Duplicate action items are detected and merged automatically, preventing me from seeing the same item multiple times.

## Assumptions

- I have active accounts for Gmail, WhatsApp, and LinkedIn that the system can access.
- I check my Obsidian vault regularly (at least daily) to review and approve pending actions.
- My Company_Handbook.md contains sufficient rules and preferences for the AI Employee to make reasonable recommendations.
- I have the necessary permissions and credentials to allow the system to send emails, post to LinkedIn, and send WhatsApp messages on my behalf.
- The Obsidian vault is stored locally and accessible to the system at all times (or has a temporary buffer for when it's not).
- I want to maintain control over all external communications and actions through the approval workflow.
- Standard business hours apply unless otherwise specified in Company_Handbook.md (e.g., LinkedIn posts during business hours, email responses within 24 hours).
- Urgent matters are identified by keywords in messages, not by sender analysis (though sender can be a factor in Company_Handbook.md rules).

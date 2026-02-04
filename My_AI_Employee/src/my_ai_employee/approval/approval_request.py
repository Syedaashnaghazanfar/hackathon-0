"""
Approval request management for Silver Tier AI Employee.

Handles creation, validation, and lifecycle management of approval requests
for external actions requiring human-in-the-loop oversight.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, Dict, Any, List
import frontmatter
import yaml

from my_ai_employee.config import get_config
from my_ai_employee.models.approval_request import ApprovalRequestSchema


@dataclass
class ApprovalRequest:
    """
    Approval request for external actions.

    Manages the lifecycle of approval requests from creation through
    approval/rejection and archival.

    Attributes:
        action_id: Unique identifier for the action item
        action_type: Type of external action (send_email, publish_linkedin_post, etc.)
        created: Timestamp of approval request creation
        status: Current status (pending, approved, rejected)
        risk_level: Assessed risk level (low, medium, high)
        risk_factors: List of identified risk factors
        draft_content: Draft content for the action (email body, post text, etc.)
        execution_plan: MCP execution plan with server/tool details
        impact_analysis: Human-readable impact description
        blast_radius: Affected parties and scope description
        approval_criteria_checklist: List of approval criteria with status
        approved_by: Username of approver (set on approval)
        approved_at: Timestamp of approval (set on approval)
        rejected_by: Username of rejector (set on rejection)
        rejected_at: Timestamp of rejection (set on rejection)
        rejection_reason: Human-provided reason for rejection
    """

    action_id: str
    action_type: Literal["send_email", "publish_linkedin_post", "send_whatsapp_message", "browser_automation"]
    created: datetime
    status: Literal["pending", "approved", "rejected"]
    risk_level: Literal["low", "medium", "high"]
    risk_factors: List[str] = field(default_factory=list)
    draft_content: str = ""
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    impact_analysis: str = ""
    blast_radius: str = ""
    approval_criteria_checklist: List[str] = field(default_factory=list)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    def to_schema(self) -> ApprovalRequestSchema:
        """
        Convert to ApprovalRequestSchema for serialization.

        Returns:
            ApprovalRequestSchema instance
        """
        return ApprovalRequestSchema(
            action_id=self.action_id,
            action_type=self.action_type,
            created=self.created,
            status=self.status,
            risk_level=self.risk_level,
            risk_factors=self.risk_factors,
        )

    def approve(self, approved_by: str) -> None:
        """
        Mark approval request as approved.

        Args:
            approved_by: Username of the approver

        Raises:
            ValueError: If request is not in pending status
        """
        if self.status != "pending":
            raise ValueError(f"Cannot approve request with status '{self.status}'")

        self.status = "approved"
        self.approved_by = approved_by
        self.approved_at = datetime.now()

    def reject(self, rejected_by: str, reason: str) -> None:
        """
        Mark approval request as rejected.

        Args:
            rejected_by: Username of the rejector
            reason: Human-readable reason for rejection

        Raises:
            ValueError: If request is not in pending status
        """
        if self.status != "pending":
            raise ValueError(f"Cannot reject request with status '{self.status}'")

        self.status = "rejected"
        self.rejected_by = rejected_by
        self.rejected_at = datetime.now()
        self.rejection_reason = reason


def create_approval_request(
    action_id: str,
    action_type: Literal["send_email", "publish_linkedin_post", "send_whatsapp_message", "browser_automation"],
    risk_level: Literal["low", "medium", "high"],
    risk_factors: List[str],
    draft_content: str,
    execution_plan: Dict[str, Any],
    impact_analysis: str,
    blast_radius: str,
    approval_criteria_checklist: List[str],
) -> ApprovalRequest:
    """
    Create a new approval request.

    Args:
        action_id: Unique identifier for the action item
        action_type: Type of external action
        risk_level: Assessed risk level
        risk_factors: List of identified risk factors
        draft_content: Draft content for the action
        execution_plan: MCP execution plan with server/tool details
        impact_analysis: Human-readable impact description
        blast_radius: Affected parties and scope description
        approval_criteria_checklist: List of approval criteria with status

    Returns:
        ApprovalRequest instance

    Example:
        >>> request = create_approval_request(
        ...     action_id="20260123-email-abc123",
        ...     action_type="send_email",
        ...     risk_level="high",
        ...     risk_factors=["External email", "Contains financial data"],
        ...     draft_content="Subject: Re: Q4 Report\\n\\nHi John,...",
        ...     execution_plan={"mcp_server": "email", "tool_name": "send_email", ...},
        ...     impact_analysis="Sending quarterly financial report to external contact",
        ...     blast_radius="Single recipient (john@company.com), professional context",
        ...     approval_criteria_checklist=["☐ Recipient trust verified", "☐ Content accuracy checked"],
        ... )
    """
    return ApprovalRequest(
        action_id=action_id,
        action_type=action_type,
        created=datetime.now(),
        status="pending",
        risk_level=risk_level,
        risk_factors=risk_factors,
        draft_content=draft_content,
        execution_plan=execution_plan,
        impact_analysis=impact_analysis,
        blast_radius=blast_radius,
        approval_criteria_checklist=approval_criteria_checklist,
    )


def write_approval_request_to_vault(
    approval_request: ApprovalRequest,
    vault_path: Optional[Path] = None,
) -> Path:
    """
    Write approval request to Pending_Approval/ folder in vault.

    Creates a markdown file with YAML frontmatter containing approval request
    metadata and a human-readable body with risk assessment and execution preview.

    Args:
        approval_request: ApprovalRequest instance to write
        vault_path: Path to vault root (defaults to config.vault_root)

    Returns:
        Path to created approval request file

    Example:
        >>> request = create_approval_request(...)
        >>> path = write_approval_request_to_vault(request)
        >>> print(path)
        AI_Employee_Vault/Pending_Approval/20260123-email-abc123-approval.md
    """
    if vault_path is None:
        config = get_config()
        vault_path = config.vault_root

    pending_approval_dir = vault_path / "Pending_Approval"
    pending_approval_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = f"{approval_request.action_id}-approval.md"
    filepath = pending_approval_dir / filename

    # Build frontmatter
    frontmatter_dict = {
        "type": "approval_request",
        "action_id": approval_request.action_id,
        "action_type": approval_request.action_type,
        "created": approval_request.created.isoformat(),
        "status": approval_request.status,
        "risk_level": approval_request.risk_level,
        "risk_factors": approval_request.risk_factors,
    }

    # Build body content
    body_lines = [
        f"# Approval Request: {approval_request.action_id}",
        "",
        "## Action Classification",
        f"- **Action Type**: {approval_request.action_type}",
        f"- **Risk Level**: {approval_request.risk_level.upper()}",
        f"- **Status**: {approval_request.status}",
        "",
        "## Risk Assessment",
        "",
        "### Risk Factors",
    ]

    for factor in approval_request.risk_factors:
        body_lines.append(f"- {factor}")

    body_lines.extend([
        "",
        "### Impact Analysis",
        approval_request.impact_analysis,
        "",
        "### Blast Radius",
        approval_request.blast_radius,
        "",
        "## Approval Criteria Checklist",
        "",
    ])

    for criterion in approval_request.approval_criteria_checklist:
        body_lines.append(criterion)

    body_lines.extend([
        "",
        "## Draft Content",
        "",
        "```",
        approval_request.draft_content,
        "```",
        "",
        "## Execution Plan",
        "",
        "```yaml",
        yaml.dump(approval_request.execution_plan, default_flow_style=False, sort_keys=False),
        "```",
        "",
        "---",
        "",
        "## Approval Instructions",
        "",
        "**To Approve**: Move this file to `/Approved/` folder",
        "**To Reject**: Move this file to `/Rejected/` folder and add rejection reason in a `## Rejection Reason` section",
        "",
        f"**Created**: {approval_request.created.strftime('%Y-%m-%d %H:%M:%S')}",
    ])

    body = "\n".join(body_lines)

    # Create frontmatter document
    post = frontmatter.Post(body, **frontmatter_dict)

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    return filepath


def move_to_approved(
    approval_request: ApprovalRequest,
    approved_by: str,
    vault_path: Optional[Path] = None,
) -> Path:
    """
    Move approval request from Pending_Approval/ to Approved/ folder.

    Args:
        approval_request: ApprovalRequest instance to approve
        approved_by: Username of the approver
        vault_path: Path to vault root (defaults to config.vault_root)

    Returns:
        Path to approved request file in Approved/ folder

    Raises:
        FileNotFoundError: If pending approval file not found
    """
    if vault_path is None:
        config = get_config()
        vault_path = config.vault_root

    # Update approval request
    approval_request.approve(approved_by)

    # Source and destination paths
    pending_path = vault_path / "Pending_Approval" / f"{approval_request.action_id}-approval.md"
    approved_dir = vault_path / "Approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    approved_path = approved_dir / f"{approval_request.action_id}-approved.md"

    if not pending_path.exists():
        raise FileNotFoundError(f"Pending approval file not found: {pending_path}")

    # Read existing content
    with open(pending_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    # Update frontmatter
    post.metadata["status"] = "approved"
    post.metadata["approved_by"] = approved_by
    post.metadata["approved_at"] = approval_request.approved_at.isoformat()

    # Append approval confirmation to body
    post.content += f"\n\n---\n\n## Approval Confirmation\n\n✅ **Approved by**: {approved_by}\n**Approved at**: {approval_request.approved_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Write to approved location
    with open(approved_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # Remove from pending
    pending_path.unlink()

    return approved_path


def move_to_rejected(
    approval_request: ApprovalRequest,
    rejected_by: str,
    rejection_reason: str,
    vault_path: Optional[Path] = None,
) -> Path:
    """
    Move approval request from Pending_Approval/ to Rejected/ folder.

    Args:
        approval_request: ApprovalRequest instance to reject
        rejected_by: Username of the rejector
        rejection_reason: Human-readable reason for rejection
        vault_path: Path to vault root (defaults to config.vault_root)

    Returns:
        Path to rejected request file in Rejected/ folder

    Raises:
        FileNotFoundError: If pending approval file not found
    """
    if vault_path is None:
        config = get_config()
        vault_path = config.vault_root

    # Update approval request
    approval_request.reject(rejected_by, rejection_reason)

    # Source and destination paths
    pending_path = vault_path / "Pending_Approval" / f"{approval_request.action_id}-approval.md"
    rejected_dir = vault_path / "Rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    rejected_path = rejected_dir / f"{approval_request.action_id}-rejected.md"

    if not pending_path.exists():
        raise FileNotFoundError(f"Pending approval file not found: {pending_path}")

    # Read existing content
    with open(pending_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    # Update frontmatter
    post.metadata["status"] = "rejected"
    post.metadata["rejected_by"] = rejected_by
    post.metadata["rejected_at"] = approval_request.rejected_at.isoformat()
    post.metadata["rejection_reason"] = rejection_reason

    # Append rejection notice to body
    post.content += f"\n\n---\n\n## Rejection Notice\n\n❌ **Rejected by**: {rejected_by}\n**Rejected at**: {approval_request.rejected_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n**Reason**: {rejection_reason}\n"

    # Write to rejected location
    with open(rejected_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # Remove from pending
    pending_path.unlink()

    return rejected_path


def validate_approval_request(approval_request: ApprovalRequest) -> tuple[bool, list[str]]:
    """
    Validate approval request for completeness and correctness.

    Args:
        approval_request: ApprovalRequest instance to validate

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> request = create_approval_request(...)
        >>> is_valid, errors = validate_approval_request(request)
        >>> if not is_valid:
        ...     print(f"Validation errors: {errors}")
    """
    errors = []

    # Required fields
    if not approval_request.action_id:
        errors.append("action_id is required")

    if not approval_request.action_type:
        errors.append("action_type is required")

    if not approval_request.risk_level:
        errors.append("risk_level is required")

    # Draft content required for external actions
    if not approval_request.draft_content:
        errors.append("draft_content is required for external actions")

    # Execution plan required
    if not approval_request.execution_plan:
        errors.append("execution_plan is required")
    else:
        # Validate execution plan structure
        required_plan_keys = ["mcp_server", "tool_name", "tool_inputs"]
        for key in required_plan_keys:
            if key not in approval_request.execution_plan:
                errors.append(f"execution_plan missing required key: {key}")

    # Impact analysis required for medium/high risk
    if approval_request.risk_level in ["medium", "high"] and not approval_request.impact_analysis:
        errors.append("impact_analysis is required for medium/high risk actions")

    # Blast radius required for high risk
    if approval_request.risk_level == "high" and not approval_request.blast_radius:
        errors.append("blast_radius is required for high risk actions")

    # Approval criteria checklist required
    if not approval_request.approval_criteria_checklist:
        errors.append("approval_criteria_checklist is required")

    return len(errors) == 0, errors

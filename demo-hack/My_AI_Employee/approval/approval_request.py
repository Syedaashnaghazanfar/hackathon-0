"""
Approval workflow module for Silver Tier AI Employee.
Handles creation, validation, and movement of approval requests.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ApprovalRequest:
    """
    Manages approval requests for external actions.

    Handles the lifecycle of approval requests:
    - Creation in Pending_Approval/
    - Validation of request format
    - Movement between folders (Pending → Approved/Rejected)
    """

    def __init__(self, vault_root: str):
        """
        Initialize approval request manager.

        Args:
            vault_root: Path to Obsidian vault root
        """
        self.vault_root = Path(vault_root)
        self.pending_approval = self.vault_root / 'Pending_Approval'
        self.approved = self.vault_root / 'Approved'
        self.rejected = self.vault_root / 'Rejected'

        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.rejected.mkdir(parents=True, exist_ok=True)

    def create(self, action_item_path: Path, plan_content: str, draft_content: str) -> Optional[Path]:
        """
        Create approval request from action item and plan.

        Args:
            action_item_path: Path to original action item
            plan_content: Plan markdown content
            draft_content: Draft action content (email, post, message)

        Returns:
            Path to created approval request, or None if creation failed
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            action_type = self._extract_action_type(action_item_path)
            filename = f"{timestamp}_approval_{action_type}.md"
            approval_path = self.pending_approval / filename

            # Create approval request content
            content = f"""# Approval Request: {action_type.replace('_', ' ').title()}

**Created**: {datetime.now().isoformat()}
**Source**: {action_item_path.name}
**Status**: Pending Approval

---

## Plan

{plan_content}

---

## Draft Action

{draft_content}

---

## Approval Instructions

**To Approve**: Move this file to `Approved/` folder
**To Reject**: Move this file to `Rejected/` folder (optionally add rejection reason below)

## Rejection Reason (if applicable)

<!-- Add your rejection reason here -->

---

## Metadata

- Original action item: {action_item_path.name}
- Created: {datetime.now().isoformat()}
- Requires approval: Yes
"""

            # Write approval request
            with open(approval_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Created approval request: {filename}")
            return approval_path

        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return None

    def validate(self, approval_path: Path) -> bool:
        """
        Validate approval request format.

        Args:
            approval_path: Path to approval request file

        Returns:
            True if valid, False otherwise
        """
        try:
            if not approval_path.exists():
                logger.error(f"Approval request not found: {approval_path}")
                return False

            # Read content
            with open(approval_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for required sections
            required_sections = ['## Plan', '## Draft Action', '## Approval Instructions']
            for section in required_sections:
                if section not in content:
                    logger.error(f"Missing required section: {section}")
                    return False

            logger.debug(f"Approval request validated: {approval_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error validating approval request: {e}")
            return False

    def move_to_approved(self, approval_path: Path) -> Optional[Path]:
        """
        Move approval request to Approved/ folder.

        Args:
            approval_path: Path to approval request in Pending_Approval/

        Returns:
            New path in Approved/ folder, or None if move failed
        """
        try:
            if not self.validate(approval_path):
                logger.error("Cannot move invalid approval request")
                return None

            # Generate new path
            new_path = self.approved / approval_path.name

            # Move file
            approval_path.rename(new_path)

            logger.info(f"Moved to Approved: {approval_path.name}")
            return new_path

        except Exception as e:
            logger.error(f"Error moving to Approved: {e}")
            return None

    def move_to_rejected(self, approval_path: Path, reason: Optional[str] = None) -> Optional[Path]:
        """
        Move approval request to Rejected/ folder.

        Args:
            approval_path: Path to approval request in Pending_Approval/
            reason: Optional rejection reason

        Returns:
            New path in Rejected/ folder, or None if move failed
        """
        try:
            # Add rejection reason if provided
            if reason:
                with open(approval_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Add rejection reason
                content = content.replace(
                    '<!-- Add your rejection reason here -->',
                    f"**Rejected**: {datetime.now().isoformat()}\n\n{reason}"
                )

                with open(approval_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Generate new path
            new_path = self.rejected / approval_path.name

            # Move file
            approval_path.rename(new_path)

            logger.info(f"Moved to Rejected: {approval_path.name}")
            return new_path

        except Exception as e:
            logger.error(f"Error moving to Rejected: {e}")
            return None

    def _extract_action_type(self, action_item_path: Path) -> str:
        """
        Extract action type from action item filename.

        Args:
            action_item_path: Path to action item

        Returns:
            Action type string (email, linkedin_post, whatsapp, etc.)
        """
        filename = action_item_path.name.lower()

        if 'email' in filename:
            return 'email'
        elif 'linkedin' in filename:
            return 'linkedin_post'
        elif 'whatsapp' in filename:
            return 'whatsapp'
        else:
            return 'unknown'

    def get_pending_count(self) -> int:
        """
        Get count of pending approval requests.

        Returns:
            Number of files in Pending_Approval/
        """
        try:
            return len(list(self.pending_approval.glob('*.md')))
        except Exception as e:
            logger.error(f"Error counting pending approvals: {e}")
            return 0

    def get_approved_count(self) -> int:
        """
        Get count of approved requests.

        Returns:
            Number of files in Approved/
        """
        try:
            return len(list(self.approved.glob('*.md')))
        except Exception as e:
            logger.error(f"Error counting approved requests: {e}")
            return 0

    def get_rejected_count(self) -> int:
        """
        Get count of rejected requests.

        Returns:
            Number of files in Rejected/
        """
        try:
            return len(list(self.rejected.glob('*.md')))
        except Exception as e:
            logger.error(f"Error counting rejected requests: {e}")
            return 0

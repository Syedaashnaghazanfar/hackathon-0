"""
Dashboard updater for Silver Tier AI Employee.

Updates Dashboard.md with real-time statistics and recent activity.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import re

from my_ai_employee.config import get_config


class DashboardUpdater:
    """
    Updates Dashboard.md with system statistics and activity.

    Maintains sections for:
    - Pending approvals count
    - Recent activity log
    - Success/failure counts
    - System health status
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize dashboard updater.

        Args:
            vault_path: Path to vault root (defaults to config.vault_root)
        """
        if vault_path is None:
            config = get_config()
            vault_path = config.vault_root

        self.vault_path = vault_path
        self.dashboard_path = vault_path / "Dashboard.md"

        # Ensure Dashboard.md exists
        if not self.dashboard_path.exists():
            self._create_default_dashboard()

    def _create_default_dashboard(self) -> None:
        """
        Create default Dashboard.md with initial structure.
        """
        default_content = """# AI Employee Dashboard

Last updated: {timestamp}

## System Status

- **Status**: 🟢 Running
- **Mode**: Production
- **Uptime**: {uptime}

## Pending Actions

### Awaiting Approval
- **Pending Approvals**: 0 action(s) in `/Pending_Approval/`

### In Progress
- **Needs Action**: 0 item(s) in `/Needs_Action/`

## Recent Activity

### Last 10 Actions
<!-- Recent activity entries will appear here -->

## Statistics (Last 24 Hours)

- **Actions Processed**: 0
- **✅ Successful**: 0
- **❌ Failed**: 0
- **⏳ Pending Approval**: 0

## Notes

Add any manual notes or observations here. This section will be preserved across updates.

""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), uptime="0 seconds")

        with open(self.dashboard_path, 'w', encoding='utf-8') as f:
            f.write(default_content)

    def update_pending_count(self) -> None:
        """
        Update pending approval count in Dashboard.md.

        Counts files in /Pending_Approval/ and updates the dashboard.
        """
        pending_dir = self.vault_path / "Pending_Approval"
        pending_count = len(list(pending_dir.glob("*-approval.md"))) if pending_dir.exists() else 0

        needs_action_dir = self.vault_path / "Needs_Action"
        needs_action_count = len(list(needs_action_dir.glob("*.md"))) if needs_action_dir.exists() else 0

        # Read current dashboard
        content = self._read_dashboard()

        # Update pending approvals count
        content = re.sub(
            r'\*\*Pending Approvals\*\*: \d+ action\(s\)',
            f'**Pending Approvals**: {pending_count} action(s)',
            content
        )

        # Update needs action count
        content = re.sub(
            r'\*\*Needs Action\*\*: \d+ item\(s\)',
            f'**Needs Action**: {needs_action_count} item(s)',
            content
        )

        # Update timestamp
        content = self._update_timestamp(content)

        # Write back
        self._write_dashboard(content)

    def add_recent_activity(
        self,
        action_id: str,
        action_type: str,
        status: str,
        description: str = "",
    ) -> None:
        """
        Add recent activity entry to Dashboard.md.

        Args:
            action_id: Unique action identifier
            action_type: Type of action (send_email, publish_linkedin_post, etc.)
            status: Execution status (success, failed, approved, rejected)
            description: Optional human-readable description
        """
        # Read current dashboard
        content = self._read_dashboard()

        # Format status emoji
        status_emoji = {
            "success": "✅",
            "failed": "❌",
            "approved": "👍",
            "rejected": "👎",
            "pending": "⏳",
        }.get(status, "ℹ️")

        # Create activity entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"- {status_emoji} **{action_type}** ({action_id}) - {status} - {timestamp}"
        if description:
            entry += f"\n  - {description}"

        # Find the Recent Activity section
        activity_pattern = r'(### Last 10 Actions\s*\n<!-- Recent activity entries will appear here -->)'
        match = re.search(activity_pattern, content)

        if match:
            # Insert new entry after the comment
            insertion_point = match.end()
            content = content[:insertion_point] + f"\n{entry}" + content[insertion_point:]

            # Keep only last 10 entries
            activity_section = re.search(
                r'### Last 10 Actions.*?(?=\n## |\Z)',
                content,
                re.DOTALL
            )
            if activity_section:
                lines = activity_section.group().split('\n')
                # Keep header + comment + 10 entries
                entries = [line for line in lines if line.strip().startswith('-')]
                if len(entries) > 10:
                    entries = entries[:10]
                    # Reconstruct section
                    new_section = '\n'.join(lines[:2] + entries)
                    content = content[:activity_section.start()] + new_section + content[activity_section.end():]

        # Update timestamp
        content = self._update_timestamp(content)

        # Write back
        self._write_dashboard(content)

    def update_statistics(
        self,
        actions_processed: int = 0,
        successful: int = 0,
        failed: int = 0,
        pending: int = 0,
    ) -> None:
        """
        Update statistics section in Dashboard.md.

        Args:
            actions_processed: Total actions processed
            successful: Number of successful actions
            failed: Number of failed actions
            pending: Number of pending approvals
        """
        # Read current dashboard
        content = self._read_dashboard()

        # Update statistics
        content = re.sub(
            r'\*\*Actions Processed\*\*: \d+',
            f'**Actions Processed**: {actions_processed}',
            content
        )
        content = re.sub(
            r'\*\*✅ Successful\*\*: \d+',
            f'**✅ Successful**: {successful}',
            content
        )
        content = re.sub(
            r'\*\*❌ Failed\*\*: \d+',
            f'**❌ Failed**: {failed}',
            content
        )
        content = re.sub(
            r'\*\*⏳ Pending Approval\*\*: \d+',
            f'**⏳ Pending Approval**: {pending}',
            content
        )

        # Update timestamp
        content = self._update_timestamp(content)

        # Write back
        self._write_dashboard(content)

    def add_warning(self, warning_message: str) -> None:
        """
        Add warning to Dashboard.md.

        Args:
            warning_message: Warning message to display
        """
        # Read current dashboard
        content = self._read_dashboard()

        # Check if Warnings section exists
        if "## Warnings" not in content:
            # Add Warnings section before Notes
            notes_pattern = r'(## Notes)'
            match = re.search(notes_pattern, content)
            if match:
                warnings_section = "\n## Warnings\n\n<!-- System warnings will appear here -->\n\n"
                content = content[:match.start()] + warnings_section + content[match.start():]

        # Add warning entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        warning_entry = f"- ⚠️ **{timestamp}**: {warning_message}"

        # Find Warnings section and add entry
        warnings_pattern = r'(## Warnings\s*\n<!-- System warnings will appear here -->)'
        match = re.search(warnings_pattern, content)
        if match:
            insertion_point = match.end()
            content = content[:insertion_point] + f"\n{warning_entry}" + content[insertion_point:]

        # Update timestamp
        content = self._update_timestamp(content)

        # Write back
        self._write_dashboard(content)

    def _read_dashboard(self) -> str:
        """
        Read current Dashboard.md content.

        Returns:
            Dashboard content as string
        """
        if not self.dashboard_path.exists():
            self._create_default_dashboard()

        with open(self.dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _write_dashboard(self, content: str) -> None:
        """
        Write Dashboard.md content.

        Args:
            content: Dashboard content to write
        """
        with open(self.dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_timestamp(self, content: str) -> str:
        """
        Update last updated timestamp in dashboard.

        Args:
            content: Dashboard content

        Returns:
            Updated content with new timestamp
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return re.sub(
            r'Last updated: .*',
            f'Last updated: {timestamp}',
            content
        )

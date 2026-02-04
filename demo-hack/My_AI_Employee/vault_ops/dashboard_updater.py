"""
Dashboard updater for vault operations.

Updates Dashboard.md with system status, pending counts, recent activity,
and warnings while preserving user notes.
"""

from pathlib import Path
from datetime import datetime
import logging
import re
import subprocess
import json


logger = logging.getLogger(__name__)


class DashboardUpdater:
    """
    Manages updates to the Dashboard.md file.

    Provides non-destructive updates that preserve user-added content
    while updating system-managed sections.
    """

    def __init__(self, vault_path: str | Path):
        """
        Initialize dashboard updater.

        Args:
            vault_path: Path to the Obsidian vault root

        Raises:
            ValueError: If vault_path is invalid
        """
        self.vault_path = Path(vault_path)

        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        self.dashboard_path = self.vault_path / "Dashboard.md"

        if not self.dashboard_path.exists():
            logger.warning(f"Dashboard not found, will create: {self.dashboard_path}")
            self._create_default_dashboard()

    def _create_default_dashboard(self) -> None:
        """Create a default dashboard if it doesn't exist."""
        default_content = """# AI Employee Dashboard

## Status Overview
**Pending Items**: 0
**Last Updated**: Never

## Silver Tier Status
**Pending Approvals**: 0
**Approved (Ready to Execute)**: 0
**Rejected**: 0
**Failed**: 0

## Watcher Status
- Gmail: Not started
- LinkedIn: Not started
- WhatsApp: Not started

## Recent Activity
No activity yet.

## System Health
✅ System operational

## Warnings
No warnings.

---
## User Notes
<!-- Add your notes below this line. They will be preserved during updates. -->

"""
        self.dashboard_path.write_text(default_content, encoding='utf-8')
        logger.info("Created default dashboard")

    def _read_dashboard(self) -> str:
        """Read current dashboard content."""
        try:
            return self.dashboard_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read dashboard: {e}")
            return ""

    def _write_dashboard(self, content: str) -> None:
        """Write updated dashboard content."""
        try:
            self.dashboard_path.write_text(content, encoding='utf-8')
            logger.debug("Dashboard updated successfully")
        except Exception as e:
            logger.error(f"Failed to write dashboard: {e}")
            raise

    def _update_section(self, content: str, section_name: str, new_section_content: str) -> str:
        """
        Update a specific section in the dashboard.

        Preserves content after the user notes separator.

        Args:
            content: Current dashboard content
            section_name: Name of the section to update (e.g., "Status Overview")
            new_section_content: New content for the section

        Returns:
            Updated dashboard content
        """
        # Find the section
        section_pattern = rf'(## {re.escape(section_name)}.*?)(?=\n## |\n---|\Z)'

        if re.search(section_pattern, content, re.DOTALL):
            # Replace existing section
            updated = re.sub(
                section_pattern,
                f'## {section_name}\n{new_section_content}\n',
                content,
                flags=re.DOTALL
            )
            return updated
        else:
            # Section doesn't exist, add it before user notes separator
            separator_index = content.find('---')
            if separator_index != -1:
                before_separator = content[:separator_index]
                after_separator = content[separator_index:]
                return f"{before_separator}## {section_name}\n{new_section_content}\n\n{after_separator}"
            else:
                # No separator, append to end
                return f"{content}\n## {section_name}\n{new_section_content}\n"

    def update_pending_count(self, count: int) -> None:
        """
        Update the pending items count in the dashboard.

        Args:
            count: Number of pending items in Needs_Action folder
        """
        content = self._read_dashboard()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status_content = f"""**Pending Items**: {count}
**Last Updated**: {timestamp}"""

        updated_content = self._update_section(content, "Status Overview", status_content)
        self._write_dashboard(updated_content)

        logger.info(f"Updated pending count: {count}")

    def add_recent_activity(self, activity_description: str, item_reference: str = None) -> None:
        """
        Add a recent activity entry to the dashboard.

        Args:
            activity_description: Description of the activity
            item_reference: Optional reference to related item
        """
        content = self._read_dashboard()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build activity entry
        if item_reference:
            activity_entry = f"- **{timestamp}**: {activity_description} (`{item_reference}`)"
        else:
            activity_entry = f"- **{timestamp}**: {activity_description}"

        # Extract current recent activity section
        activity_pattern = r'## Recent Activity\n(.*?)(?=\n## |\n---|\Z)'
        match = re.search(activity_pattern, content, re.DOTALL)

        if match:
            current_activities = match.group(1).strip()

            # Remove "No activity yet" message if present
            if "No activity yet" in current_activities:
                current_activities = ""

            # Add new activity at the top
            if current_activities:
                activities_list = current_activities.split('\n')
                activities_list.insert(0, activity_entry)

                # Keep only last 10 activities
                activities_list = activities_list[:10]

                new_activities = '\n'.join(activities_list)
            else:
                new_activities = activity_entry
        else:
            new_activities = activity_entry

        updated_content = self._update_section(content, "Recent Activity", new_activities)
        self._write_dashboard(updated_content)

        logger.info(f"Added activity: {activity_description}")

    def add_warning(self, warning_message: str, warning_id: str = None) -> None:
        """
        Add a warning to the dashboard.

        Args:
            warning_message: Warning message to display
            warning_id: Optional unique ID for the warning (for deduplication)
        """
        content = self._read_dashboard()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build warning entry
        warning_entry = f"⚠️ **{timestamp}**: {warning_message}"

        if warning_id:
            warning_entry += f" (ID: {warning_id})"

        # Extract current warnings section
        warnings_pattern = r'## Warnings\n(.*?)(?=\n## |\n---|\Z)'
        match = re.search(warnings_pattern, content, re.DOTALL)

        if match:
            current_warnings = match.group(1).strip()

            # Remove "No warnings" message if present
            if "No warnings" in current_warnings:
                current_warnings = ""

            # Check for duplicate warning_id
            if warning_id and warning_id in current_warnings:
                logger.debug(f"Warning {warning_id} already exists, skipping")
                return

            # Add new warning
            if current_warnings:
                new_warnings = f"{warning_entry}\n{current_warnings}"
            else:
                new_warnings = warning_entry
        else:
            new_warnings = warning_entry

        updated_content = self._update_section(content, "Warnings", new_warnings)
        self._write_dashboard(updated_content)

        logger.info(f"Added warning: {warning_message[:50]}...")

    def clear_warnings(self) -> None:
        """Clear all warnings from the dashboard."""
        content = self._read_dashboard()

        warnings_content = "No warnings."

        updated_content = self._update_section(content, "Warnings", warnings_content)
        self._write_dashboard(updated_content)

        logger.info("Cleared all warnings")

    def update_system_health(self, status: str, details: str = None) -> None:
        """
        Update system health status.

        Args:
            status: Health status ("operational", "degraded", "error")
            details: Optional details about the status
        """
        content = self._read_dashboard()

        # Map status to emoji
        status_emoji = {
            'operational': '✅',
            'degraded': '⚠️',
            'error': '❌'
        }

        emoji = status_emoji.get(status.lower(), '❓')

        health_content = f"{emoji} System {status}"

        if details:
            health_content += f"\n\n{details}"

        updated_content = self._update_section(content, "System Health", health_content)
        self._write_dashboard(updated_content)

        logger.info(f"Updated system health: {status}")

    def get_dashboard_summary(self) -> dict:
        """
        Get a summary of current dashboard state.

        Returns:
            Dictionary with dashboard summary information
        """
        content = self._read_dashboard()

        # Extract pending count
        pending_match = re.search(r'\*\*Pending Items\*\*:\s*(\d+)', content)
        pending_count = int(pending_match.group(1)) if pending_match else 0

        # Count warnings
        warnings_section = re.search(r'## Warnings\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        warning_count = 0
        if warnings_section:
            warnings_text = warnings_section.group(1)
            if "No warnings" not in warnings_text:
                warning_count = warnings_text.count('⚠️')

        # Count recent activities
        activity_section = re.search(r'## Recent Activity\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        activity_count = 0
        if activity_section:
            activities_text = activity_section.group(1)
            if "No activity yet" not in activities_text:
                activity_count = activities_text.count('- **')

        return {
            'pending_count': pending_count,
            'warning_count': warning_count,
            'activity_count': activity_count,
            'dashboard_path': str(self.dashboard_path)
        }

    def get_pm2_watcher_statuses(self) -> dict:
        """
        Query PM2 for watcher process statuses.

        Returns:
            Dictionary mapping watcher types to their PM2 status information.
            Returns empty dict if PM2 is not available or no watchers are running.
        """
        watcher_statuses = {}

        try:
            # Run pm2 jlist to get JSON output of all processes
            pm2_output = subprocess.run(
                ['pm2', 'jlist'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if pm2_output.returncode != 0:
                logger.debug("PM2 not available or returned error")
                return watcher_statuses

            pm2_processes = json.loads(pm2_output.stdout)

            # Map PM2 process names to watcher types
            pm2_name_map = {
                'gmail-watcher': 'gmail',
                'whatsapp-watcher': 'whatsapp',
                'linkedin-watcher': 'linkedin',
                'filesystem-watcher': 'filesystem',
                'orchestrator': 'orchestrator'
            }

            for process in pm2_processes:
                pm2_name = process.get('name', '')
                watcher_type = pm2_name_map.get(pm2_name)

                if watcher_type:
                    # Get PM2 metadata
                    pm2_env = process.get('pm2_env', {})
                    monit = process.get('monit', {})

                    status = pm2_env.get('status', 'unknown')
                    restart_count = pm2_env.get('restart_time', 0)
                    uptime_ms = monit.get('uptime', 0)
                    uptime_seconds = uptime_ms // 1000 if uptime_ms else 0

                    # Format uptime display
                    if uptime_seconds < 60:
                        uptime_display = f"{uptime_seconds}s"
                    elif uptime_seconds < 3600:
                        uptime_display = f"{uptime_seconds // 60}m"
                    elif uptime_seconds < 86400:
                        hours = uptime_seconds // 3600
                        minutes = (uptime_seconds % 3600) // 60
                        uptime_display = f"{hours}h {minutes}m"
                    else:
                        days = uptime_seconds // 86400
                        hours = (uptime_seconds % 86400) // 3600
                        uptime_display = f"{days}d {hours}h"

                    # Determine stability label based on restart count
                    if restart_count == 0:
                        stability_label = "Stable"
                    elif restart_count <= 2:
                        stability_label = "Good"
                    elif restart_count <= 5:
                        stability_label = "Fair"
                    else:
                        stability_label = "Unstable"

                    watcher_statuses[watcher_type] = {
                        'status': 'running' if status == 'online' else 'stopped',
                        'pm2_status': status,
                        'restart_count': restart_count,
                        'uptime_seconds': uptime_seconds,
                        'uptime_display': uptime_display,
                        'stability_label': stability_label,
                        'pm2_id': process.get('pm_id', ''),
                        'memory_mb': monit.get('memory', 0) // (1024 * 1024),
                        'cpu_percent': monit.get('cpu', 0)
                    }

        except subprocess.TimeoutExpired:
            logger.warning("PM2 query timed out")
        except subprocess.SubprocessError as e:
            logger.debug(f"PM2 subprocess error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PM2 JSON output: {e}")
        except FileNotFoundError:
            logger.debug("PM2 command not found (not installed or not in PATH)")
        except Exception as e:
            logger.error(f"Unexpected error querying PM2: {e}")

        return watcher_statuses


def update_dashboard_after_triage(
    vault_path: str | Path,
    pending_count: int,
    processed_items: list,
    warnings: list = None
) -> None:
    """
    Update dashboard after triage workflow completes.

    Args:
        vault_path: Path to the Obsidian vault root
        pending_count: Current count of pending items
        processed_items: List of processed item names
        warnings: Optional list of warning messages
    """
    updater = DashboardUpdater(vault_path)

    # Update pending count
    updater.update_pending_count(pending_count)

    # Add activity for each processed item
    for item_name in processed_items:
        updater.add_recent_activity(
            "Processed action item",
            item_reference=item_name
        )

    # Add warnings if any
    if warnings:
        for warning in warnings:
            updater.add_warning(warning)

    # Update system health
    if warnings:
        updater.update_system_health("degraded", f"{len(warnings)} warning(s) require attention")
    else:
        updater.update_system_health("operational")

    logger.info("Dashboard updated after triage")


def update_silver_tier_status(
    vault_path: str | Path,
    pending_approvals: int = None,
    approved_count: int = None,
    rejected_count: int = None,
    failed_count: int = None
) -> None:
    """
    Update Silver tier approval workflow status.

    Args:
        vault_path: Path to the Obsidian vault root
        pending_approvals: Count of items in Pending_Approval folder
        approved_count: Count of items in Approved folder
        rejected_count: Count of items in Rejected folder
        failed_count: Count of items in Failed folder
    """
    updater = DashboardUpdater(vault_path)
    content = updater._read_dashboard()

    # Build status content
    status_lines = []
    if pending_approvals is not None:
        status_lines.append(f"**Pending Approvals**: {pending_approvals}")
    if approved_count is not None:
        status_lines.append(f"**Approved (Ready to Execute)**: {approved_count}")
    if rejected_count is not None:
        status_lines.append(f"**Rejected**: {rejected_count}")
    if failed_count is not None:
        status_lines.append(f"**Failed**: {failed_count}")

    if status_lines:
        status_content = '\n'.join(status_lines)
        updated_content = updater._update_section(content, "Silver Tier Status", status_content)
        updater._write_dashboard(updated_content)
        logger.info("Updated Silver tier status")


def update_watcher_status(
    vault_path: str | Path,
    gmail_status: str = None,
    linkedin_status: str = None,
    whatsapp_status: str = None,
    use_pm2: bool = True
) -> None:
    """
    Update watcher status in dashboard.

    If no statuses are provided and use_pm2=True, automatically queries PM2
    for real-time watcher status.

    Args:
        vault_path: Path to the Obsidian vault root
        gmail_status: Gmail watcher status (running, stopped, error)
        linkedin_status: LinkedIn watcher status (running, stopped, error)
        whatsapp_status: WhatsApp watcher status (running, stopped, error)
        use_pm2: If True and no statuses provided, query PM2 for status
    """
    updater = DashboardUpdater(vault_path)
    content = updater._read_dashboard()

    # If no statuses provided and use_pm2 is True, query PM2
    if use_pm2 and all(s is None for s in [gmail_status, linkedin_status, whatsapp_status]):
        pm2_statuses = updater.get_pm2_watcher_statuses()

        if pm2_statuses:
            # Use PM2 data
            gmail_status = pm2_statuses.get('gmail', {}).get('status', 'not_started')
            linkedin_status = pm2_statuses.get('linkedin', {}).get('status', 'not_started')
            whatsapp_status = pm2_statuses.get('whatsapp', {}).get('status', 'not_started')

            # Build enhanced status with PM2 metadata
            status_lines = []
            for watcher_type, watcher_name in [('gmail', 'Gmail'), ('linkedin', 'LinkedIn'), ('whatsapp', 'WhatsApp')]:
                if watcher_type in pm2_statuses:
                    data = pm2_statuses[watcher_type]
                    status = data['status']
                    uptime = data['uptime_display']
                    stability = data['stability_label']
                    restart_count = data['restart_count']

                    # Map status to emoji
                    emoji = '✅' if status == 'running' else '⏸️' if status == 'stopped' else '❌'

                    # Build status line with metadata
                    status_line = f"- {watcher_name}: {emoji} {status.title()}"
                    if status == 'running':
                        status_line += f" (Uptime: {uptime}, Restarts: {restart_count}, {stability})"

                    status_lines.append(status_line)
                else:
                    status_lines.append(f"- {watcher_name}: ⚪ Not started")

            if status_lines:
                watcher_content = '\n'.join(status_lines)
                updated_content = updater._update_section(content, "Watcher Status", watcher_content)
                updater._write_dashboard(updated_content)
                logger.info("Updated watcher status from PM2")
                return

    # Fallback to manual status (original behavior)
    status_emoji = {
        'running': '✅',
        'stopped': '⏸️',
        'error': '❌',
        'not_started': '⚪'
    }

    # Build watcher status content
    status_lines = []
    if gmail_status is not None:
        emoji = status_emoji.get(gmail_status.lower(), '❓')
        status_lines.append(f"- Gmail: {emoji} {gmail_status.title()}")
    if linkedin_status is not None:
        emoji = status_emoji.get(linkedin_status.lower(), '❓')
        status_lines.append(f"- LinkedIn: {emoji} {linkedin_status.title()}")
    if whatsapp_status is not None:
        emoji = status_emoji.get(whatsapp_status.lower(), '❓')
        status_lines.append(f"- WhatsApp: {emoji} {whatsapp_status.title()}")

    if status_lines:
        watcher_content = '\n'.join(status_lines)
        updated_content = updater._update_section(content, "Watcher Status", watcher_content)
        updater._write_dashboard(updated_content)
        logger.info("Updated watcher status")

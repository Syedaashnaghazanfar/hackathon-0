"""
Audit logger for Silver Tier AI Employee.

Provides structured JSON logging to /Logs/YYYY-MM-DD.json with credential sanitization.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from my_ai_employee.config import get_config
from my_ai_employee.models import AuditLogEntrySchema


logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logger for recording all external actions with credential sanitization.

    Logs are written to /Logs/YYYY-MM-DD.json (one file per day, append-only).
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize audit logger.

        Args:
            vault_path: Path to vault root (defaults to config.vault_root)
        """
        if vault_path is None:
            config = get_config()
            vault_path = config.vault_root

        self.vault_path = vault_path
        self.logs_dir = vault_path / "Logs"

        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log_execution(
        self,
        action_type: str,
        execution_status: str,
        executor: str,
        executor_id: str,
        tool_name: str,
        tool_inputs_sanitized: Dict[str, Any],
        approval_reason: Optional[str] = None,
        approval_id: Optional[str] = None,
        mcp_server: str = "",
        error: Optional[str] = None,
        retry_count: int = 0,
    ) -> None:
        """
        Log an action execution to the daily audit log.

        Args:
            action_type: Type of action (send_email, publish_linkedin_post, etc.)
            execution_status: Status (success, failed, dry_run)
            executor: Who executed (human, ai_employee)
            executor_id: User ID or "claude-code"
            tool_name: MCP tool name
            tool_inputs_sanitized: Sanitized tool inputs (credentials redacted)
            approval_reason: Optional approval reason
            approval_id: Optional approval request ID
            mcp_server: MCP server name
            error: Optional error message
            retry_count: Number of retries attempted

        Example:
            >>> logger = AuditLogger()
            >>> logger.log_execution(
            ...     action_type="send_email",
            ...     execution_status="success",
            ...     executor="ai_employee",
            ...     executor_id="claude-code",
            ...     tool_name="send_email",
            ...     tool_inputs_sanitized={"to": "user@example.com", "subject": "Test"},
            ...     mcp_server="email"
            ... )
        """
        # Create audit log entry
        entry = AuditLogEntrySchema(
            timestamp=datetime.now(),
            action_type=action_type,
            execution_status=execution_status,
            executor=executor,
            executor_id=executor_id,
            tool_name=tool_name,
            tool_inputs_sanitized=tool_inputs_sanitized,
            approval_reason=approval_reason,
            approval_id=approval_id,
            mcp_server=mcp_server,
            error=error,
            retry_count=retry_count,
        )

        # Get daily log file path
        log_file = self._get_daily_log_file()

        # Append to log file
        try:
            # Load existing entries
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            else:
                entries = []

            # Append new entry
            entries.append(entry.to_dict())

            # Write back
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)

            logger.info(f"Audit log entry written to {log_file.name}")

        except Exception as e:
            logger.error(f"Failed to write audit log entry: {e}", exc_info=True)

    def _get_daily_log_file(self) -> Path:
        """
        Get path to today's log file.

        Returns:
            Path to /Logs/YYYY-MM-DD.json
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return self.logs_dir / f"{today}.json"

    def get_logs_for_date(self, date_str: str) -> list[Dict[str, Any]]:
        """
        Get all log entries for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            List of audit log entry dictionaries

        Example:
            >>> logger = AuditLogger()
            >>> entries = logger.get_logs_for_date("2026-01-22")
            >>> len(entries)
            5
        """
        log_file = self.logs_dir / f"{date_str}.json"

        if not log_file.exists():
            return []

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read log file {log_file}: {e}")
            return []

    def get_recent_logs(self, days: int = 7) -> list[Dict[str, Any]]:
        """
        Get all log entries from the last N days.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of audit log entry dictionaries (newest first)

        Example:
            >>> logger = AuditLogger()
            >>> recent = logger.get_recent_logs(days=3)
            >>> len(recent)
            15
        """
        all_entries = []

        # Get all log files sorted by date (newest first)
        log_files = sorted(self.logs_dir.glob("*.json"), reverse=True)

        # Read up to N days
        for log_file in log_files[:days]:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    all_entries.extend(entries)
            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {e}")

        return all_entries

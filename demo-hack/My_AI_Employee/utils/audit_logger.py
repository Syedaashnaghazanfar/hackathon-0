"""
Audit logging utility for Silver tier external actions.
Logs to JSONL files in Logs/YYYY-MM-DD.json.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .sanitizer import CredentialSanitizer


class AuditLogger:
    """Log all AI Employee actions with sanitized credentials."""

    def __init__(self, vault_root: str = "My_AI_Employee/AI_Employee_Vault"):
        self.vault_root = Path(vault_root)
        self.log_dir = self.vault_root / "Logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure JSON logging
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_dir / "audit.log")
            handler.setFormatter(logging.Formatter('%(message)s'))  # JSON only
            self.logger.addHandler(handler)

    def _today_file(self) -> Path:
        """Path to today's JSONL log file."""
        return self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    def _generate_entry_id(self) -> str:
        """Generate a unique ID for each audit entry."""
        return f"audit_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"

    def _sanitize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize credentials in audit entry."""
        sanitized = CredentialSanitizer.sanitize_dict(entry)
        return sanitized

    def log_action_requested(self, action_type: str, source_system: str,
                              action_details: Dict[str, Any],
                              requires_approval: bool = False) -> str:
        """Log when action is first created/requested."""
        entry_id = self._generate_entry_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        entry = {
            "timestamp": timestamp,
            "entry_id": entry_id,
            "event_type": "action_requested",
            "action_type": action_type,
            "source_system": source_system,
            "actor": "ai_employee",
            "action_details": action_details,
            "approval_info": {"requires_approval": requires_approval},
            "status": "pending",
        }

        self._write_entry(entry)
        return entry_id

    def log_action_approved(self, entry_id: str, action_type: str,
                            approved_by: str, approval_reason: str,
                            approval_duration_seconds: int) -> None:
        """Log when action is approved."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        entry = {
            "timestamp": timestamp,
            "entry_id": entry_id,
            "event_type": "action_approved",
            "action_type": action_type,
            "source_system": "approval_workflow",
            "actor": approved_by,
            "approval_info": {
                "approved_by": approved_by,
                "approval_action": "approved",
                "approved_at": timestamp,
                "approval_reason": approval_reason,
                "approval_duration_seconds": approval_duration_seconds,
            },
            "status": "approved",
        }

        self._write_entry(entry)

    def log_action_executed(self, entry_id: str, action_type: str,
                            mcp_server: str, execution_time_ms: int,
                            success: bool, result: Optional[Dict] = None,
                            error: Optional[str] = None) -> None:
        """Log when action is executed."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        entry = {
            "timestamp": timestamp,
            "entry_id": entry_id,
            "event_type": "action_executed" if success else "action_failed",
            "action_type": action_type,
            "source_system": "mcp_executor",
            "actor": "ai_employee",
            "execution_info": {
                "mcp_server": mcp_server,
                "execution_time_ms": execution_time_ms,
                "status": "success" if success else "failed",
                "result": result,
                "error": error,
                "will_retry": bool(error and not success),
            },
            "status": "executed",
        }

        self._write_entry(entry)

    def log_action_rejected(self, entry_id: str, action_type: str,
                            rejected_by: str, rejection_reason: str) -> None:
        """Log when action is rejected."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        entry = {
            "timestamp": timestamp,
            "entry_id": entry_id,
            "event_type": "action_rejected",
            "action_type": action_type,
            "source_system": "approval_workflow",
            "actor": rejected_by,
            "approval_info": {
                "approved_by": rejected_by,
                "approval_action": "rejected",
                "approved_at": timestamp,
                "approval_reason": rejection_reason,
            },
            "status": "rejected",
        }

        self._write_entry(entry)

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write sanitized entry to JSONL log."""
        sanitized = self._sanitize_entry(entry)
        log_line = json.dumps(sanitized, ensure_ascii=False)

        # Write to JSONL file
        log_file = self._today_file()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')

        # Also log to Python logger
        self.logger.info(log_line)

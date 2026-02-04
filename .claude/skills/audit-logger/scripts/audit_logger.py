#!/usr/bin/env python3
"""Audit Logger - Log all AI Employee actions with credentials sanitization."""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import re

from dotenv import load_dotenv

load_dotenv()

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Only the message (which will be JSON)
    handlers=[
        logging.FileHandler('logs/audit.log'),
    ]
)
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)


class CredentialSanitizer:
    """Sanitize sensitive credentials from logs."""

    # Patterns to redact
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'api_key': r'(?i)(api[_-]?key|apikey|access[_-]?token|token)["\']?\s*[=:]\s*["\']?[A-Za-z0-9\-_.~+/]+=*["\']?',
        'jwt': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.?[A-Za-z0-9_-]*',
        'ssh_key': r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |DSA |EC )?PRIVATE KEY-----',
    }

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email address."""
        if not email or '@' not in email:
            return email
        local, domain = email.split('@', 1)
        return f"{local[:1]}****@{'*' * len(domain.split('.')[0])}.{domain.split('.')[-1]}"

    @staticmethod
    def sanitize_token(token: str, length: int = 20) -> str:
        """Sanitize API token or JWT."""
        if not token or len(token) < 10:
            return token
        return f"{token[:length]}*** (token redacted)"

    @staticmethod
    def sanitize_credit_card(card: str) -> str:
        """Sanitize credit card number (PAN)."""
        digits_only = re.sub(r'\D', '', card)
        if len(digits_only) < 12:
            return card
        return f"{digits_only[:4]} **** **** {digits_only[-4:]}"

    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize a dictionary."""
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            # Check if key suggests sensitive data
            key_lower = key.lower()

            if isinstance(value, dict):
                sanitized[key] = CredentialSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    CredentialSanitizer.sanitize_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            elif isinstance(value, str):
                if 'email' in key_lower or 'recipient' in key_lower:
                    sanitized[key] = CredentialSanitizer.sanitize_email(value)
                elif 'token' in key_lower or 'api_key' in key_lower or 'password' in key_lower:
                    sanitized[key] = CredentialSanitizer.sanitize_token(value)
                elif 'card' in key_lower or 'credit' in key_lower:
                    sanitized[key] = CredentialSanitizer.sanitize_credit_card(value)
                elif 'body' in key_lower and len(value) > 100:
                    # Truncate large body text in logs
                    sanitized[key] = f"{value[:100]}... (truncated)"
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value

        return sanitized


class AuditLogger:
    """Log all AI Employee actions."""

    def __init__(self):
        self.vault_root = Path(os.getenv('VAULT_ROOT', 'My_AI_Employee/AI_Employee_Vault'))

    def _generate_action_id(self, action_type: str, timestamp: str) -> str:
        """Generate unique action ID."""
        time_str = timestamp.split('T')[1][:8].replace(':', '')
        hash_input = f"{action_type}_{timestamp}_{os.urandom(4).hex()}"
        hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:6]
        return f"{action_type}_{timestamp.split('T')[0].replace('-', '')}_{time_str}_{hash_val}"

    def log_action_requested(self, action_type: str, source_system: str,
                            action_details: Dict[str, Any],
                            requires_approval: bool = False) -> str:
        """Log when action is first created/requested."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        action_id = self._generate_action_id(action_type, timestamp)

        log_entry = {
            "timestamp": timestamp,
            "event_type": "action_requested",
            "action_id": action_id,
            "action_type": action_type,
            "source_system": source_system,
            "actor": "ai_employee",
            "action_details": CredentialSanitizer.sanitize_dict(action_details),
            "approval_info": {
                "approval_required": requires_approval,
            },
            "compliance": {
                "external_action": action_details.get('external', False),
                "requires_approval": requires_approval,
            }
        }

        self._write_audit_log(log_entry)
        return action_id

    def log_action_approved(self, action_id: str, action_type: str,
                           approved_by: str, approval_reason: str,
                           approval_duration_seconds: int) -> None:
        """Log when action is approved."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        log_entry = {
            "timestamp": timestamp,
            "event_type": "action_approved",
            "action_id": action_id,
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
            "compliance": {
                "approved": True,
            }
        }

        self._write_audit_log(log_entry)

    def log_action_executed(self, action_id: str, action_type: str,
                           mcp_server: str, execution_time_ms: int,
                           success: bool, result: Optional[Dict] = None,
                           error: Optional[str] = None) -> None:
        """Log when action is executed."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        log_entry = {
            "timestamp": timestamp,
            "event_type": "action_executed" if success else "action_failed",
            "action_id": action_id,
            "action_type": action_type,
            "source_system": "mcp_executor",
            "actor": "ai_employee",
            "execution_info": {
                "mcp_server": mcp_server,
                "execution_time_ms": execution_time_ms,
                "status": "success" if success else "failed",
            }
        }

        if result:
            log_entry["execution_info"]["result"] = CredentialSanitizer.sanitize_dict(result)

        if error:
            log_entry["execution_info"]["error_message"] = error
            log_entry["execution_info"]["will_retry"] = True

        self._write_audit_log(log_entry)

    def log_action_rejected(self, action_id: str, action_type: str,
                           rejected_by: str, rejection_reason: str) -> None:
        """Log when action is rejected."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        log_entry = {
            "timestamp": timestamp,
            "event_type": "action_rejected",
            "action_id": action_id,
            "action_type": action_type,
            "source_system": "approval_workflow",
            "actor": rejected_by,
            "approval_info": {
                "approved_by": rejected_by,
                "approval_action": "rejected",
                "approved_at": timestamp,
                "approval_reason": rejection_reason,
            },
            "compliance": {
                "approved": False,
            }
        }

        self._write_audit_log(log_entry)

    def _write_audit_log(self, entry: Dict[str, Any]) -> None:
        """Write sanitized entry to audit log."""
        # Sanitize entire entry
        sanitized_entry = CredentialSanitizer.sanitize_dict(entry)

        # Write as JSON
        audit_logger.info(json.dumps(sanitized_entry))

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary from recent audit logs."""
        if not Path('logs/audit.log').exists():
            return {}

        stats = {
            'total_actions': 0,
            'approved': 0,
            'rejected': 0,
            'executed_success': 0,
            'executed_failed': 0,
            'by_type': {},
        }

        try:
            with open('logs/audit.log', 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        event_type = entry.get('event_type')
                        action_type = entry.get('action_type')

                        if event_type == 'action_requested':
                            stats['total_actions'] += 1
                        elif event_type == 'action_approved':
                            stats['approved'] += 1
                        elif event_type == 'action_rejected':
                            stats['rejected'] += 1
                        elif event_type == 'action_executed':
                            stats['executed_success'] += 1
                        elif event_type == 'action_failed':
                            stats['executed_failed'] += 1

                        if action_type:
                            stats['by_type'][action_type] = stats['by_type'].get(action_type, 0) + 1
                    except json.JSONDecodeError:
                        pass

        except FileNotFoundError:
            pass

        return stats


# Global instance
logger_instance = AuditLogger()


def log_action_requested(action_type: str, source_system: str,
                        action_details: Dict[str, Any],
                        requires_approval: bool = False) -> str:
    """Module-level function to log action requested."""
    return logger_instance.log_action_requested(action_type, source_system, action_details, requires_approval)


def log_action_approved(action_id: str, action_type: str, approved_by: str,
                       approval_reason: str, approval_duration_seconds: int) -> None:
    """Module-level function to log action approved."""
    logger_instance.log_action_approved(action_id, action_type, approved_by, approval_reason, approval_duration_seconds)


def log_action_executed(action_id: str, action_type: str, mcp_server: str,
                       execution_time_ms: int, success: bool,
                       result: Optional[Dict] = None, error: Optional[str] = None) -> None:
    """Module-level function to log action executed."""
    logger_instance.log_action_executed(action_id, action_type, mcp_server, execution_time_ms, success, result, error)


def log_action_rejected(action_id: str, action_type: str, rejected_by: str,
                       rejection_reason: str) -> None:
    """Module-level function to log action rejected."""
    logger_instance.log_action_rejected(action_id, action_type, rejected_by, rejection_reason)

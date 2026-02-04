"""
Unit tests for audit logger.

Tests the AuditLogger class functionality including credential sanitization.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime
import json
import sys

# Add My_AI_Employee to path (go up to My_AI_Employee root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.audit_logger import AuditLogger
from utils.sanitizer import CredentialSanitizer


@pytest.fixture
def mock_logs_path(tmp_path):
    """Create a temporary logs directory."""
    logs = tmp_path / "Logs"
    logs.mkdir()
    return logs


@pytest.fixture
def audit_logger(mock_logs_path):
    """Create an AuditLogger instance."""
    sanitizer = CredentialSanitizer()
    return AuditLogger(logs_path=mock_logs_path, sanitizer=sanitizer)


def test_audit_logger_initialization(mock_logs_path):
    """Test AuditLogger initializes correctly."""
    sanitizer = CredentialSanitizer()
    logger = AuditLogger(logs_path=mock_logs_path, sanitizer=sanitizer)

    assert logger.logs_path == mock_logs_path
    assert logger.sanitizer is not None


def test_audit_logger_creates_log_file(audit_logger, mock_logs_path):
    """Test that audit logger creates log file."""
    entry_id = audit_logger.log_execution(
        action_type='send_email',
        actor='claude-code',
        target='test@example.com',
        result='success'
    )

    # Check log file exists
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = mock_logs_path / f"{today}.json"
    assert log_file.exists()


def test_audit_logger_sanitizes_credentials(audit_logger):
    """Test that credentials are sanitized in logs."""
    parameters = {
        'to': 'test@example.com',
        'password': 'secret123',
        'api_key': 'sk_test_1234567890abcdef',
        'body': 'Test message'
    }

    entry_id = audit_logger.log_execution(
        action_type='send_email',
        actor='claude-code',
        target='test@example.com',
        parameters=parameters,
        result='success'
    )

    # Read log file
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = audit_logger.logs_path / f"{today}.json"
    content = log_file.read_text()

    # Verify credentials are sanitized
    assert 'secret123' not in content
    assert '***REDACTED***' in content or 'sk_t...cdef' in content


def test_audit_logger_log_format(audit_logger, mock_logs_path):
    """Test that log entries have correct format."""
    entry_id = audit_logger.log_execution(
        action_type='send_email',
        actor='claude-code',
        target='test@example.com',
        result='success',
        approval_status='approved',
        approval_by='user'
    )

    # Read log file
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = mock_logs_path / f"{today}.json"
    content = log_file.read_text()
    data = json.loads(content)

    # Verify structure
    assert 'entries' in data
    assert len(data['entries']) > 0

    entry = data['entries'][0]
    assert 'timestamp' in entry
    assert 'action_type' in entry
    assert 'actor' in entry
    assert 'target' in entry
    assert 'result' in entry
    assert entry['action_type'] == 'send_email'


def test_audit_logger_multiple_entries(audit_logger, mock_logs_path):
    """Test logging multiple entries to same file."""
    # Log multiple entries
    for i in range(3):
        audit_logger.log_execution(
            action_type='send_email',
            actor='claude-code',
            target=f'test{i}@example.com',
            result='success'
        )

    # Read log file
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = mock_logs_path / f"{today}.json"
    content = log_file.read_text()
    data = json.loads(content)

    # Verify all entries are present
    assert len(data['entries']) == 3


def test_credential_sanitizer_email():
    """Test that email addresses are sanitized correctly."""
    sanitizer = CredentialSanitizer()

    result = sanitizer.sanitize_email('user@example.com')
    assert result == 'u***@example.com'


def test_credential_sanitizer_token():
    """Test that tokens are sanitized correctly."""
    sanitizer = CredentialSanitizer()

    token = 'sk_test_1234567890abcdefghijklmnop'
    result = sanitizer.sanitize_token(token)
    assert result.startswith('sk_t')
    assert result.endswith('mnop')
    assert '...' in result


def test_credential_sanitizer_dict():
    """Test that dictionaries are sanitized recursively."""
    sanitizer = CredentialSanitizer()

    data = {
        'email': 'user@example.com',
        'password': 'secret123',
        'nested': {
            'api_key': 'sk_test_1234567890',
            'message': 'Hello world'
        }
    }

    result = sanitizer.sanitize(data)

    assert result['password'] == '***REDACTED***'
    assert result['nested']['api_key'] != 'sk_test_1234567890'
    assert result['nested']['message'] == 'Hello world'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

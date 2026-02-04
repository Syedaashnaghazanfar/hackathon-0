"""Shared utilities for AI Employee (Bronze + Silver tier)."""

# Bronze tier utilities (backward compatibility)
from .frontmatter_utils import load_action_item, save_action_item
from .dedupe_state import DedupeTracker

# Silver tier utilities
from .deduplication import compute_content_hash, is_duplicate, add_to_processed
from .vault_operations import (
    get_vault_root,
    read_markdown_with_frontmatter,
    write_markdown_with_frontmatter,
    move_file,
    list_files_in_folder,
    ensure_folder_structure,
    get_action_item_path,
)
from .retry import exponential_backoff_retry, retry_with_backoff
from .logging_config import (
    setup_logging,
    log_heartbeat,
    log_action_item_created,
    log_execution_result,
    log_dry_run_mode,
)
from .sanitizer import (
    redact_api_key,
    redact_oauth_token,
    redact_pii,
    sanitize_tool_inputs,
    sanitize_error_message,
)
from .auth_helper import OAuth2Helper

__all__ = [
    # Bronze tier (backward compatibility)
    "load_action_item",
    "save_action_item",
    "DedupeTracker",
    # Silver tier - Deduplication
    "compute_content_hash",
    "is_duplicate",
    "add_to_processed",
    # Silver tier - Vault operations
    "get_vault_root",
    "read_markdown_with_frontmatter",
    "write_markdown_with_frontmatter",
    "move_file",
    "list_files_in_folder",
    "ensure_folder_structure",
    "get_action_item_path",
    # Silver tier - Retry logic
    "exponential_backoff_retry",
    "retry_with_backoff",
    # Silver tier - Logging
    "setup_logging",
    "log_heartbeat",
    "log_action_item_created",
    "log_execution_result",
    "log_dry_run_mode",
    # Silver tier - Sanitization
    "redact_api_key",
    "redact_oauth_token",
    "redact_pii",
    "sanitize_tool_inputs",
    "sanitize_error_message",
    # Silver tier - Authentication
    "OAuth2Helper",
]

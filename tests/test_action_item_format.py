"""Tests for action item formatting and frontmatter structure.

Validates that action items follow the contract defined in
specs/001-bronze-ai-employee/contracts/vault-artifacts.md
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import pytest

from My_AI_Employee.src.my_ai_employee.utils import (
    load_action_item,
    save_action_item,
)


def test_action_item_has_required_frontmatter():
    """Test that action items contain all required frontmatter fields.

    Required fields per contract:
    - type: file_drop|email|manual
    - received: ISO 8601 timestamp
    - status: pending|processed
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        action_item_path = Path(tmpdir) / "test_item.md"

        # Create action item with required fields
        metadata = {
            "type": "file_drop",
            "received": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        content = "# Test Action Item\n\nThis is a test."
        post = frontmatter.Post(content, **metadata)

        # Save and reload
        save_action_item(action_item_path, post)
        loaded_post = load_action_item(action_item_path)

        # Verify required fields exist
        assert "type" in loaded_post.metadata
        assert "received" in loaded_post.metadata
        assert "status" in loaded_post.metadata

        # Verify field values
        assert loaded_post["type"] in ["file_drop", "email", "manual"]
        assert loaded_post["status"] in ["pending", "processed"]


def test_action_item_received_is_iso_timestamp():
    """Test that the 'received' field is a valid ISO 8601 timestamp."""
    with tempfile.TemporaryDirectory() as tmpdir:
        action_item_path = Path(tmpdir) / "test_item.md"

        # Create action item with ISO timestamp
        now = datetime.now(timezone.utc)
        metadata = {
            "type": "file_drop",
            "received": now.isoformat(),
            "status": "pending",
        }
        content = "# Test Action Item"
        post = frontmatter.Post(content, **metadata)

        # Save and reload
        save_action_item(action_item_path, post)
        loaded_post = load_action_item(action_item_path)

        # Verify timestamp can be parsed
        received_str = loaded_post["received"]
        parsed_time = datetime.fromisoformat(received_str)

        # Verify it's a datetime object
        assert isinstance(parsed_time, datetime)

        # Verify it's close to the original time (within 1 second)
        # Handle both timezone-aware and naive datetimes
        if parsed_time.tzinfo is None:
            now_compare = now.replace(tzinfo=None)
        else:
            now_compare = now
        time_diff = abs((parsed_time - now_compare).total_seconds())
        assert time_diff < 1.0


def test_file_drop_references_original_path():
    """Test that file_drop action items reference the original file path.

    Per FR-006: Must include a reference to the original dropped file path.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        action_item_path = Path(tmpdir) / "test_item.md"
        original_file_path = "/path/to/original/file.txt"

        # Create file_drop action item
        metadata = {
            "type": "file_drop",
            "received": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        content = f"# File Drop\n\nOriginal file: `{original_file_path}`"
        post = frontmatter.Post(content, **metadata)

        # Save and reload
        save_action_item(action_item_path, post)
        loaded_post = load_action_item(action_item_path)

        # Verify type is file_drop
        assert loaded_post["type"] == "file_drop"

        # Verify content references original path
        assert original_file_path in loaded_post.content


def test_frontmatter_preservation_on_load_dump():
    """Test that frontmatter is preserved when loading and saving.

    Per FR-014: Archive operations must preserve YAML frontmatter.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        action_item_path = Path(tmpdir) / "test_item.md"

        # Create action item with multiple fields
        metadata = {
            "type": "file_drop",
            "received": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "priority": "high",
            "source_id": "test123",
            "custom_field": "custom_value",
        }
        content = "# Test Action Item\n\nOriginal content."
        post = frontmatter.Post(content, **metadata)

        # Save
        save_action_item(action_item_path, post)

        # Load
        loaded_post = load_action_item(action_item_path)

        # Modify and save again
        loaded_post["status"] = "processed"
        loaded_post["processed"] = datetime.now(timezone.utc).isoformat()
        save_action_item(action_item_path, loaded_post)

        # Load again
        final_post = load_action_item(action_item_path)

        # Verify all original fields are preserved
        assert final_post["type"] == metadata["type"]
        assert final_post["received"] == metadata["received"]
        assert final_post["priority"] == metadata["priority"]
        assert final_post["source_id"] == metadata["source_id"]
        assert final_post["custom_field"] == metadata["custom_field"]

        # Verify new fields were added
        assert final_post["status"] == "processed"
        assert "processed" in final_post.metadata

        # Verify content is preserved
        assert "Original content" in final_post.content


def test_optional_frontmatter_fields():
    """Test that optional frontmatter fields are handled correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        action_item_path = Path(tmpdir) / "test_item.md"

        # Create minimal action item (only required fields)
        metadata = {
            "type": "manual",
            "received": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        content = "# Minimal Item"
        post = frontmatter.Post(content, **metadata)

        # Save and reload
        save_action_item(action_item_path, post)
        loaded_post = load_action_item(action_item_path)

        # Verify required fields exist
        assert "type" in loaded_post.metadata
        assert "received" in loaded_post.metadata
        assert "status" in loaded_post.metadata

        # Add optional fields
        loaded_post["priority"] = "medium"
        loaded_post["from"] = "user@example.com"
        save_action_item(action_item_path, loaded_post)

        # Reload and verify
        final_post = load_action_item(action_item_path)
        assert final_post["priority"] == "medium"
        assert final_post["from"] == "user@example.com"

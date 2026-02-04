"""
Tests for action item format validation (User Story 5).

Validates that action items follow the standardized frontmatter contract
for reliable triage and processing.
"""

import pytest
from pathlib import Path
from datetime import datetime
import frontmatter
from utils.frontmatter_utils import (
    create_action_item,
    save_action_item,
    load_action_item,
    validate_action_item
)


@pytest.fixture
def temp_action_item(tmp_path):
    """Create a temporary action item file for testing."""
    action_file = tmp_path / "test_action.md"

    # Create a test action item
    post = create_action_item(
        content="Test action item content",
        item_type="file_drop",
        status="pending",
        source_path="/test/path/file.txt"
    )

    save_action_item(post, action_file)
    return action_file


def test_action_item_has_required_frontmatter(temp_action_item):
    """
    Test that action items have all required frontmatter fields.

    Required fields: type, received, status
    """
    # Load the action item
    post = load_action_item(temp_action_item)

    # Verify required fields exist
    assert 'type' in post.metadata, "Missing required field: type"
    assert 'received' in post.metadata, "Missing required field: received"
    assert 'status' in post.metadata, "Missing required field: status"

    # Verify field values are valid
    assert post['type'] in ['file_drop', 'email', 'manual'], f"Invalid type: {post['type']}"
    assert post['status'] in ['pending', 'processed'], f"Invalid status: {post['status']}"

    # Verify validation passes
    is_valid, error = validate_action_item(post)
    assert is_valid, f"Action item validation failed: {error}"


def test_action_item_received_is_iso_timestamp():
    """
    Test that the 'received' field is a valid ISO 8601 timestamp.

    Format: YYYY-MM-DDTHH:MM:SS.ffffff
    """
    # Create action item
    post = create_action_item(
        content="Test content",
        item_type="file_drop",
        status="pending"
    )

    # Verify received field exists
    assert 'received' in post.metadata, "Missing 'received' field"

    received = post['received']

    # Verify it's a string
    assert isinstance(received, str), f"'received' should be string, got {type(received)}"

    # Verify it can be parsed as ISO 8601 timestamp
    try:
        parsed_date = datetime.fromisoformat(received)
        assert parsed_date is not None, "Failed to parse ISO timestamp"
    except ValueError as e:
        pytest.fail(f"'received' is not a valid ISO 8601 timestamp: {received} - {e}")

    # Verify timestamp is recent (within last minute)
    now = datetime.now()
    time_diff = abs((now - parsed_date).total_seconds())
    assert time_diff < 60, f"Timestamp is not recent: {received}"


def test_file_drop_references_original_path(tmp_path):
    """
    Test that file_drop action items reference the original file path (FR-006).

    The action item should contain a reference to the source file path.
    """
    source_path = "/test/watch/folder/document.pdf"

    # Create action item with source path
    post = create_action_item(
        content="Test file drop action",
        item_type="file_drop",
        status="pending",
        source_path=source_path
    )

    # Verify source_path is in metadata
    assert 'source_path' in post.metadata, "Missing 'source_path' field"
    assert post['source_path'] == source_path, f"Source path mismatch: {post['source_path']}"

    # Save and reload to verify persistence
    action_file = tmp_path / "test_file_drop.md"
    save_action_item(post, action_file)

    reloaded = load_action_item(action_file)
    assert reloaded['source_path'] == source_path, "Source path not preserved after save/load"


def test_frontmatter_preservation_on_load_dump(tmp_path):
    """
    Test that frontmatter is preserved when loading and dumping action items.

    All metadata fields should be preserved exactly, including custom fields.
    """
    # Create action item with multiple fields
    original_post = create_action_item(
        content="Original content\n\nWith multiple lines",
        item_type="file_drop",
        status="pending",
        source_path="/test/file.txt",
        custom_field="custom_value",
        priority="high",
        tags=["test", "important"]
    )

    # Save to file
    action_file = tmp_path / "test_preservation.md"
    save_action_item(original_post, action_file)

    # Load from file
    loaded_post = load_action_item(action_file)

    # Verify all original fields are preserved
    assert loaded_post['type'] == original_post['type']
    assert loaded_post['status'] == original_post['status']
    assert loaded_post['source_path'] == original_post['source_path']
    assert loaded_post['custom_field'] == original_post['custom_field']
    assert loaded_post['priority'] == original_post['priority']
    assert loaded_post['tags'] == original_post['tags']

    # Verify content is preserved
    assert loaded_post.content == original_post.content

    # Modify and save again
    loaded_post['status'] = 'processed'
    loaded_post['processed_by'] = 'test_user'

    save_action_item(loaded_post, action_file)

    # Load again and verify all fields (original + new) are preserved
    final_post = load_action_item(action_file)

    assert final_post['type'] == original_post['type']
    assert final_post['status'] == 'processed'
    assert final_post['custom_field'] == original_post['custom_field']
    assert final_post['processed_by'] == 'test_user'
    assert final_post.content == original_post.content


def test_action_item_content_separate_from_frontmatter(tmp_path):
    """
    Test that markdown content is separate from frontmatter.

    Content should not include YAML frontmatter delimiters.
    """
    content = "# Test Action\n\nThis is the content.\n\n- Item 1\n- Item 2"

    post = create_action_item(
        content=content,
        item_type="manual",
        status="pending"
    )

    # Verify content doesn't contain frontmatter delimiters
    assert '---' not in post.content
    assert post.content == content

    # Save and reload
    action_file = tmp_path / "test_content.md"
    save_action_item(post, action_file)

    # Read raw file to verify format
    raw_content = action_file.read_text()

    # Verify file has frontmatter delimiters
    assert raw_content.startswith('---\n'), "File should start with frontmatter delimiter"
    assert raw_content.count('---') >= 2, "File should have opening and closing frontmatter delimiters"

    # Load and verify content is clean
    loaded = load_action_item(action_file)
    assert loaded.content == content
    assert '---' not in loaded.content


def test_invalid_action_item_validation():
    """
    Test that validation catches invalid action items.
    """
    # Missing required field
    post = frontmatter.Post("Content")
    post['type'] = 'file_drop'
    # Missing 'received' and 'status'

    is_valid, error = validate_action_item(post)
    assert not is_valid, "Should fail validation with missing fields"
    assert error is not None, "Should provide error message"

    # Invalid type
    post2 = create_action_item(
        content="Test",
        item_type="file_drop",
        status="pending"
    )
    post2['type'] = 'invalid_type'

    is_valid, error = validate_action_item(post2)
    assert not is_valid, "Should fail validation with invalid type"
    assert 'type' in error.lower(), "Error should mention 'type'"

    # Invalid status
    post3 = create_action_item(
        content="Test",
        item_type="file_drop",
        status="pending"
    )
    post3['status'] = 'invalid_status'

    is_valid, error = validate_action_item(post3)
    assert not is_valid, "Should fail validation with invalid status"
    assert 'status' in error.lower(), "Error should mention 'status'"

"""
Frontmatter utilities for action item handling.

Uses python-frontmatter to load, modify, and save markdown files
while preserving YAML frontmatter.
"""

import frontmatter
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def load_action_item(file_path: str | Path) -> frontmatter.Post:
    """
    Load an action item markdown file with frontmatter.

    Args:
        file_path: Path to the markdown file

    Returns:
        frontmatter.Post object with metadata and content

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If frontmatter is malformed
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Action item not found: {file_path}")

    try:
        post = frontmatter.load(str(file_path))
        return post
    except Exception as e:
        raise ValueError(f"Failed to parse frontmatter in {file_path}: {e}")


def save_action_item(post: frontmatter.Post, file_path: str | Path) -> None:
    """
    Save an action item to a markdown file, preserving all frontmatter.

    Args:
        post: frontmatter.Post object with metadata and content
        file_path: Destination path for the markdown file

    Raises:
        IOError: If file cannot be written
    """
    file_path = Path(file_path)

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Serialize to string first, then write
        content = frontmatter.dumps(post)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Failed to save action item to {file_path}: {e}")


def create_action_item(
    content: str,
    item_type: str,
    status: str = "pending",
    **metadata: Any
) -> frontmatter.Post:
    """
    Create a new action item Post object with required frontmatter.

    Args:
        content: Markdown content (without frontmatter)
        item_type: Type of action item (file_drop, email, manual)
        status: Status (pending, processed)
        **metadata: Additional frontmatter fields

    Returns:
        frontmatter.Post object ready to be saved
    """
    # Required frontmatter fields
    frontmatter_data = {
        'type': item_type,
        'received': datetime.now().isoformat(),
        'status': status,
    }

    # Add optional metadata
    frontmatter_data.update(metadata)

    # Create Post object
    post = frontmatter.Post(content, **frontmatter_data)

    return post


def validate_action_item(post: frontmatter.Post) -> tuple[bool, Optional[str]]:
    """
    Validate that an action item has required frontmatter fields.

    Args:
        post: frontmatter.Post object to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    required_fields = ['type', 'received', 'status']

    for field in required_fields:
        if field not in post.metadata:
            return False, f"Missing required field: {field}"

    # Validate type field
    valid_types = ['file_drop', 'email', 'manual']
    if post['type'] not in valid_types:
        return False, f"Invalid type: {post['type']}. Must be one of {valid_types}"

    # Validate status field
    valid_statuses = ['pending', 'processed']
    if post['status'] not in valid_statuses:
        return False, f"Invalid status: {post['status']}. Must be one of {valid_statuses}"

    return True, None


def update_action_item_status(
    post: frontmatter.Post,
    new_status: str,
    **additional_metadata: Any
) -> frontmatter.Post:
    """
    Update action item status and add processing metadata.

    Args:
        post: frontmatter.Post object to update
        new_status: New status value
        **additional_metadata: Additional fields to add (e.g., processed timestamp)

    Returns:
        Updated frontmatter.Post object
    """
    post['status'] = new_status

    # Add processing timestamp if moving to processed
    if new_status == 'processed' and 'processed' not in post.metadata:
        post['processed'] = datetime.now().isoformat()

    # Add any additional metadata
    for key, value in additional_metadata.items():
        post[key] = value

    return post

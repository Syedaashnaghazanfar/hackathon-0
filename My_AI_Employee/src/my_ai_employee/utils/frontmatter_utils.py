"""Utilities for reading and writing Markdown files with YAML frontmatter.

Uses python-frontmatter to safely load/save action items while preserving
metadata and content structure.
"""

from pathlib import Path
from typing import Any, Dict

import frontmatter


def load_action_item(file_path: Path | str) -> frontmatter.Post:
    """Load a Markdown file with YAML frontmatter.

    Args:
        file_path: Path to the markdown file

    Returns:
        frontmatter.Post object with metadata accessible via dict-like interface
        and content accessible via .content attribute

    Example:
        >>> post = load_action_item("Needs_Action/item.md")
        >>> print(post['type'])  # Access frontmatter field
        >>> print(post.content)  # Access markdown content
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    return post


def save_action_item(file_path: Path | str, post: frontmatter.Post) -> None:
    """Save a Markdown file with YAML frontmatter.

    Preserves all existing frontmatter fields and content structure.

    Args:
        file_path: Path where the file should be saved
        post: frontmatter.Post object to save

    Example:
        >>> post = load_action_item("Needs_Action/item.md")
        >>> post['status'] = 'processed'
        >>> save_action_item("Done/item.md", post)
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Use dumps() to get string, then write to file
    # This avoids the binary/text mode issue with frontmatter.dump()
    content = frontmatter.dumps(post)
    file_path.write_text(content, encoding="utf-8")

"""
Vault operations utility for Silver Tier AI Employee.

Provides file-based operations for Obsidian vault (read/write markdown with YAML frontmatter).
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import frontmatter


def get_vault_root() -> Path:
    """
    Get vault root directory from environment variable.

    Returns:
        Path to vault root (defaults to AI_Employee_Vault)

    Raises:
        FileNotFoundError: If vault root does not exist
    """
    vault_root = os.getenv("VAULT_ROOT", "AI_Employee_Vault")
    vault_path = Path(vault_root)

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault root not found: {vault_path}")

    return vault_path


def read_markdown_with_frontmatter(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Read markdown file with YAML frontmatter.

    Args:
        file_path: Path to markdown file

    Returns:
        Tuple of (frontmatter_dict, content_body)

    Example:
        >>> metadata, content = read_markdown_with_frontmatter(Path("test.md"))
        >>> metadata["status"]
        'pending'
        >>> content
        'This is the action item content...'
    """
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    return dict(post.metadata), post.content


def write_markdown_with_frontmatter(
    file_path: Path, metadata: Dict[str, Any], content: str
) -> None:
    """
    Write markdown file with YAML frontmatter.

    Args:
        file_path: Path to markdown file
        metadata: YAML frontmatter dictionary
        content: Markdown content body

    Example:
        >>> metadata = {"status": "pending", "priority": "high"}
        >>> content = "Action item content..."
        >>> write_markdown_with_frontmatter(Path("test.md"), metadata, content)
    """
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    post = frontmatter.Post(content, **metadata)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))


def move_file(source: Path, destination: Path) -> None:
    """
    Move file from source to destination (used for approval workflow).

    Args:
        source: Source file path
        destination: Destination file path

    Raises:
        FileNotFoundError: If source file does not exist

    Example:
        >>> move_file(
        ...     Path("AI_Employee_Vault/Pending_Approval/action.md"),
        ...     Path("AI_Employee_Vault/Approved/action.md")
        ... )
    """
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)

    source.rename(destination)


def list_files_in_folder(folder_path: Path, pattern: str = "*.md") -> list[Path]:
    """
    List all markdown files in a folder.

    Args:
        folder_path: Path to folder
        pattern: Glob pattern for file matching (defaults to *.md)

    Returns:
        List of file paths

    Example:
        >>> files = list_files_in_folder(Path("AI_Employee_Vault/Needs_Action"))
        >>> len(files)
        3
    """
    if not folder_path.exists():
        return []

    return list(folder_path.glob(pattern))


def ensure_folder_structure() -> None:
    """
    Ensure all Silver tier vault folders exist.

    Creates:
    - /Needs_Action/
    - /Pending_Approval/
    - /Approved/
    - /Rejected/
    - /Failed/
    - /Done/
    - /Logs/
    - /Plans/
    """
    vault_root = get_vault_root()

    folders = [
        "Needs_Action",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Failed",
        "Done",
        "Logs",
        "Plans",
    ]

    for folder in folders:
        folder_path = vault_root / folder
        folder_path.mkdir(parents=True, exist_ok=True)


def get_action_item_path(action_id: str, folder: str = "Needs_Action") -> Path:
    """
    Get path for action item file.

    Args:
        action_id: Unique action item identifier
        folder: Folder name (defaults to Needs_Action)

    Returns:
        Path to action item file

    Example:
        >>> get_action_item_path("20260122-150000-gmail-abc123", "Pending_Approval")
        Path('AI_Employee_Vault/Pending_Approval/20260122-150000-gmail-abc123.md')
    """
    vault_root = get_vault_root()
    return vault_root / folder / f"{action_id}.md"

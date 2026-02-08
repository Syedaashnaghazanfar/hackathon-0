#!/usr/bin/env python3
"""
Shared vault operations utility for Gold Tier AI Employee.

Provides safe read/write operations for Obsidian vault markdown files
with YAML frontmatter preservation and atomic file operations.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import frontmatter

from .error_handler import safe_default

logger = logging.getLogger(__name__)


class VaultOps:
    """Safe operations for Obsidian vault."""

    def __init__(self, vault_path: str):
        """
        Initialize vault operations.

        Args:
            vault_path: Path to Obsidian vault root
        """
        self.vault_path = Path(vault_path)

    def read_markdown(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Read markdown file with YAML frontmatter.

        Args:
            file_path: Relative path from vault root

        Returns:
            Tuple of (content, frontmatter_dict)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file has malformed YAML
        """
        full_path = self.vault_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Vault file not found: {full_path}")

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            content = post.content
            metadata = post.metadata
            return content, metadata

        except Exception as e:
            logger.error(f"Error reading vault file {full_path}: {e}")
            raise

    def write_markdown(
        self,
        file_path: str,
        content: str,
        fm_dict: Optional[Dict[str, Any]] = None,
        backup: bool = True
    ) -> None:
        """
        Write markdown file with YAML frontmatter atomically.

        Args:
            file_path: Relative path from vault root
            content: Markdown content (without frontmatter)
            fm_dict: YAML frontmatter dictionary
            backup: Create .bak backup before writing (default: True)
        """
        full_path = self.vault_path / file_path

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if requested
        if backup and full_path.exists():
            backup_path = full_path.with_suffix('.md.bak')
            shutil.copy2(full_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")

        # Prepare content with frontmatter
        post = frontmatter.Post(content, **(fm_dict or {}))

        # Write to temporary file first (atomic operation)
        temp_path = full_path.with_suffix('.md.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))

            # Rename temp file to actual file (atomic)
            temp_path.replace(full_path)

            logger.debug(f"Wrote vault file: {full_path}")

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Error writing vault file {full_path}: {e}")
            raise

    def validate_frontmatter(self, file_path: str) -> bool:
        """
        Validate YAML frontmatter in vault file.

        Args:
            file_path: Relative path from vault root

        Returns:
            True if frontmatter is valid, False otherwise
        """
        try:
            _, fm = self.read_markdown(file_path)
            return True
        except Exception as e:
            logger.warning(f"Invalid frontmatter in {file_path}: {e}")
            return False

    def move_to_done(
        self,
        source_path: str,
        done_folder: str = "Done",
        additional_frontmatter: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Move vault file to Done/ folder with updated frontmatter.

        Args:
            source_path: Relative path from vault root
            done_folder: Folder name for completed items (default: "Done")
            additional_frontmatter: Additional frontmatter fields to add

        Returns:
            Path to moved file

        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        source_full = self.vault_path / source_path

        if not source_full.exists():
            raise FileNotFoundError(f"Source file not found: {source_full}")

        # Read existing content and frontmatter
        content, fm = self.read_markdown(source_path)

        # Add additional frontmatter
        if additional_frontmatter:
            fm.update(additional_frontmatter)

        # Create destination path in Done/
        filename = source_full.name
        dest_path = self.vault_path / done_folder / filename

        # Ensure Done/ folder exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to destination with updated frontmatter
        self.write_markdown(
            str(dest_path.relative_to(self.vault_path)),
            content,
            fm,
            backup=False
        )

        # Remove source file
        source_full.unlink()

        logger.info(f"Moved {source_path} to {dest_path.relative_to(self.vault_path)}")

        return dest_path


if __name__ == "__main__":
    # Test vault operations
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        vault = VaultOps(tmpdir)

        # Test write and read
        vault.write_markdown(
            "test.md",
            "# Test Content\n\nThis is test content.",
            {"type": "test", "priority": "high"}
        )

        content, fm = vault.read_markdown("test.md")
        print(f"Content: {content}")
        print(f"Frontmatter: {fm}")

        # Test move to done
        dest = vault.move_to_done("test.md", additional_frontmatter={"completed_at": "2026-01-06"})
        print(f"Moved to: {dest}")

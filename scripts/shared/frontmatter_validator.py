#!/usr/bin/env python3
"""
Shared YAML frontmatter validator for Gold Tier AI Employee.

Provides Pydantic models for common vault metadata and validation
utilities for YAML frontmatter in markdown files.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object

logger = logging.getLogger(__name__)


if PYDANTIC_AVAILABLE:
    class VaultMetadata(BaseModel):
        """Common vault metadata model."""

        type: str = Field(description="Type of vault item (e.g., 'action_item', 'briefing')")
        status: str = Field(default="pending", description="Status (e.g., 'pending', 'completed')")
        priority: str = Field(default="medium", description="Priority (e.g., 'high', 'medium', 'low')")
        created: Optional[str] = Field(default=None, description="ISO8601 creation timestamp")
        updated: Optional[str] = Field(default=None, description="ISO8601 update timestamp")

        @validator('created', 'updated')
        def validate_timestamp(cls, v):
            if v is not None:
                try:
                    datetime.fromisoformat(v.replace('Z', ''))
                except ValueError:
                    raise ValueError(f"Invalid ISO8601 timestamp: {v}")
            return v

    class ActionItemMetadata(VaultMetadata):
        """Metadata for action items in Needs_Action/."""

        source: Optional[str] = Field(default=None, description="Source of action item")
        source_id: Optional[str] = Field(default=None, description="Unique identifier from source")
        sender: Optional[str] = Field(default=None, description="Sender or source identifier")
        subject: Optional[str] = Field(default=None, description="Subject or title")
        tags: list[str] = Field(default_factory=list, description="Classification tags")

    class BriefingMetadata(VaultMetadata):
        """Metadata for CEO briefing documents."""

        health_score: Optional[int] = Field(default=None, ge=0, le=100, description="Business health score (0-100)")
        week_number: Optional[int] = Field(default=None, ge=1, le=52, description="ISO week number")
        period: Optional[str] = Field(default=None, description="Date range covered")

else:
    # Fallback if Pydantic not available
    class VaultMetadata:
        """Fallback validator without Pydantic."""
        pass


class FrontmatterValidator:
    """Validator for YAML frontmatter in vault files."""

    def __init__(self, vault_path: str):
        """
        Initialize validator.

        Args:
            vault_path: Path to Obsidian vault root
        """
        self.vault_path = Path(vault_path)

    def validate(self, file_path: str, model_class=None) -> Tuple[bool, Optional[str]]:
        """
        Validate frontmatter in vault file.

        Args:
            file_path: Relative path from vault root
            model_class: Pydantic model class for validation (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        from .vault_ops import VaultOps

        vault_ops = VaultOps(str(self.vault_path))

        try:
            _, fm = vault_ops.read_markdown(file_path)

            if not fm:
                # No frontmatter is valid
                return True, None

            if model_class and PYDANTIC_AVAILABLE:
                try:
                    model_class(**fm)
                except Exception as e:
                    return False, f"Validation error: {str(e)}"

            # Check for common required fields
            if 'type' in fm and not fm['type']:
                return False, "Field 'type' cannot be empty"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def validate_all(self, folder: str = "Needs_Action") -> Dict[str, Any]:
        """
        Validate all markdown files in a folder.

        Args:
            folder: Folder path relative to vault root

        Returns:
            Dictionary with validation results
        """
        folder_path = self.vault_path / folder

        if not folder_path.exists():
            return {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "errors": []
            }

        results = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "errors": []
        }

        for md_file in folder_path.rglob("*.md"):
            results["total"] += 1

            is_valid, error = self.validate(str(md_file.relative_to(self.vault_path)))

            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["errors"].append({
                    "file": str(md_file.relative_to(self.vault_path)),
                    "error": error
                })

        return results


if __name__ == "__main__":
    # Test validator
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        vault = VaultOps(tmpdir)

        # Create test file with valid frontmatter
        vault.write_markdown(
            "test.md",
            "# Test",
            {"type": "action_item", "status": "pending", "priority": "high"}
        )

        # Validate
        validator = FrontmatterValidator(tmpdir)
        is_valid, error = validator.validate("test.md")

        print(f"Valid: {is_valid}")
        print(f"Error: {error}")

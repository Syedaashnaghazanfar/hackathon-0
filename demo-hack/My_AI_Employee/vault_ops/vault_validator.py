"""
Vault validator for ensuring consistent vault structure.

Validates that the Obsidian vault has all required folders and files
for predictable Bronze Tier AI Employee operations.
"""

from pathlib import Path
from typing import List, Tuple
import logging


logger = logging.getLogger(__name__)


class VaultValidator:
    """
    Validates Obsidian vault structure for Bronze Tier AI Employee.

    Ensures all required folders and files exist and are properly configured.
    """

    def __init__(self, vault_path: str | Path):
        """
        Initialize vault validator.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.validation_errors = []
        self.validation_warnings = []

    def validate_structure(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that vault has all required folders and files (FR-001).

        Checks for:
        - Required folders: Inbox/, Needs_Action/, Done/, Plans/
        - Required files: Dashboard.md, Company_Handbook.md

        Returns:
            Tuple of (is_valid, errors, warnings)
            - is_valid: True if all required elements exist
            - errors: List of error messages for missing required elements
            - warnings: List of warning messages for optional issues
        """
        self.validation_errors = []
        self.validation_warnings = []

        # Check if vault path exists
        if not self.vault_path.exists():
            self.validation_errors.append(f"Vault path does not exist: {self.vault_path}")
            return False, self.validation_errors, self.validation_warnings

        if not self.vault_path.is_dir():
            self.validation_errors.append(f"Vault path is not a directory: {self.vault_path}")
            return False, self.validation_errors, self.validation_warnings

        # Check required folders
        required_folders = ['Inbox', 'Needs_Action', 'Done', 'Plans']

        for folder_name in required_folders:
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                self.validation_errors.append(f"Required folder missing: {folder_name}/")
            elif not folder_path.is_dir():
                self.validation_errors.append(f"Required folder is not a directory: {folder_name}/")

        # Check required files
        required_files = ['Dashboard.md', 'Company_Handbook.md']

        for file_name in required_files:
            file_path = self.vault_path / file_name
            if not file_path.exists():
                self.validation_errors.append(f"Required file missing: {file_name}")
            elif not file_path.is_file():
                self.validation_errors.append(f"Required file is not a regular file: {file_name}")
            else:
                # Check if file is readable and not empty
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if len(content.strip()) == 0:
                        self.validation_warnings.append(f"Required file is empty: {file_name}")
                except Exception as e:
                    self.validation_errors.append(f"Cannot read required file {file_name}: {e}")

        # Check for .obsidian folder (optional but expected)
        obsidian_folder = self.vault_path / '.obsidian'
        if not obsidian_folder.exists():
            self.validation_warnings.append(
                ".obsidian/ folder not found - vault may not have been opened in Obsidian yet"
            )

        # Determine if validation passed
        is_valid = len(self.validation_errors) == 0

        if is_valid:
            logger.info(f"Vault structure validation passed: {self.vault_path}")
        else:
            logger.error(f"Vault structure validation failed with {len(self.validation_errors)} errors")

        return is_valid, self.validation_errors, self.validation_warnings

    def validate_plans_folder(self) -> Tuple[bool, List[str]]:
        """
        Validate Plans/ folder behavior (FR-002).

        Checks:
        - Plans/ folder exists and is writable
        - Plans can be created and read
        - No permission issues

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        plans_folder = self.vault_path / 'Plans'

        # Check if Plans folder exists
        if not plans_folder.exists():
            errors.append("Plans/ folder does not exist")
            return False, errors

        # Check if Plans folder is writable
        if not plans_folder.is_dir():
            errors.append("Plans/ is not a directory")
            return False, errors

        # Try to create a test file to verify write permissions
        test_file = plans_folder / '.vault_validator_test.tmp'

        try:
            test_file.write_text("test", encoding='utf-8')
            test_file.unlink()  # Clean up
            logger.debug("Plans/ folder is writable")
        except Exception as e:
            errors.append(f"Plans/ folder is not writable: {e}")
            return False, errors

        # Check existing plans
        existing_plans = list(plans_folder.glob("*.md"))
        logger.info(f"Found {len(existing_plans)} existing plans in Plans/")

        # Verify existing plans are readable
        unreadable_plans = []
        for plan_file in existing_plans:
            try:
                plan_file.read_text(encoding='utf-8')
            except Exception as e:
                unreadable_plans.append(f"{plan_file.name}: {e}")

        if unreadable_plans:
            errors.append(f"Some plans are not readable: {', '.join(unreadable_plans)}")
            return False, errors

        return True, errors

    def validate_folder_permissions(self) -> Tuple[bool, List[str]]:
        """
        Validate that all required folders have proper permissions.

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        required_folders = ['Inbox', 'Needs_Action', 'Done', 'Plans']

        for folder_name in required_folders:
            folder_path = self.vault_path / folder_name

            if not folder_path.exists():
                errors.append(f"{folder_name}/ does not exist")
                continue

            # Test write permission
            test_file = folder_path / '.vault_validator_test.tmp'
            try:
                test_file.write_text("test", encoding='utf-8')
                test_file.unlink()
            except Exception as e:
                errors.append(f"{folder_name}/ is not writable: {e}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_vault_statistics(self) -> dict:
        """
        Get statistics about the vault contents.

        Returns:
            Dictionary with vault statistics
        """
        stats = {
            'vault_path': str(self.vault_path),
            'exists': self.vault_path.exists(),
            'folders': {},
            'files': {}
        }

        if not self.vault_path.exists():
            return stats

        # Count items in each folder
        folders = ['Inbox', 'Needs_Action', 'Done', 'Plans']
        for folder_name in folders:
            folder_path = self.vault_path / folder_name
            if folder_path.exists():
                item_count = len(list(folder_path.glob("*.md")))
                stats['folders'][folder_name] = {
                    'exists': True,
                    'item_count': item_count
                }
            else:
                stats['folders'][folder_name] = {
                    'exists': False,
                    'item_count': 0
                }

        # Check required files
        files = ['Dashboard.md', 'Company_Handbook.md']
        for file_name in files:
            file_path = self.vault_path / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    stats['files'][file_name] = {
                        'exists': True,
                        'size': len(content),
                        'lines': len(content.split('\n'))
                    }
                except Exception:
                    stats['files'][file_name] = {
                        'exists': True,
                        'size': 0,
                        'lines': 0,
                        'error': 'Cannot read file'
                    }
            else:
                stats['files'][file_name] = {
                    'exists': False
                }

        return stats

    def create_missing_structure(self, create_folders: bool = True, create_files: bool = True) -> List[str]:
        """
        Create missing folders and files to fix validation errors.

        Args:
            create_folders: Whether to create missing folders
            create_files: Whether to create missing files

        Returns:
            List of created items
        """
        created_items = []

        # Create vault directory if it doesn't exist
        if not self.vault_path.exists():
            self.vault_path.mkdir(parents=True, exist_ok=True)
            created_items.append(str(self.vault_path))
            logger.info(f"Created vault directory: {self.vault_path}")

        # Create missing folders
        if create_folders:
            required_folders = ['Inbox', 'Needs_Action', 'Done', 'Plans']
            for folder_name in required_folders:
                folder_path = self.vault_path / folder_name
                if not folder_path.exists():
                    folder_path.mkdir(parents=True, exist_ok=True)
                    created_items.append(f"{folder_name}/")
                    logger.info(f"Created folder: {folder_name}/")

        # Create missing files
        if create_files:
            # Create Dashboard.md if missing
            dashboard_path = self.vault_path / 'Dashboard.md'
            if not dashboard_path.exists():
                default_dashboard = """# AI Employee Dashboard

## Status Overview
**Pending Items**: 0
**Last Updated**: Never

## Recent Activity
No activity yet.

## System Health
✅ System operational

## Warnings
No warnings.

---
## User Notes
<!-- Add your notes below this line. They will be preserved during updates. -->

"""
                dashboard_path.write_text(default_dashboard, encoding='utf-8')
                created_items.append('Dashboard.md')
                logger.info("Created Dashboard.md")

            # Create Company_Handbook.md if missing
            handbook_path = self.vault_path / 'Company_Handbook.md'
            if not handbook_path.exists():
                default_handbook = """# Company Handbook

## Processing Rules

### Priority Classification
- **High Priority**: Urgent items requiring immediate attention
- **Medium Priority**: Standard items for normal processing
- **Low Priority**: Routine items that can be deferred

### Communication Tone
- Professional and clear
- Concise and actionable
- Respectful and helpful

## Permission Boundaries (Bronze Tier)

### Allowed Actions
- Read and analyze files in the watch folder
- Create action items in Needs_Action/
- Generate plans in Plans/
- Update Dashboard.md
- Archive items to Done/

### Prohibited Actions
- No external API calls
- No email sending
- No file modifications outside the vault
- No access to external services
- No destructive operations without explicit approval

## Output Preferences

### Plan Format
- Use checkboxes for action items: `- [ ] Action`
- Include clear done conditions
- Link to source action items
- Document reasoning and decisions

### Documentation
- Keep plans concise but complete
- Use markdown formatting
- Include timestamps
- Reference source files with full paths
"""
                handbook_path.write_text(default_handbook, encoding='utf-8')
                created_items.append('Company_Handbook.md')
                logger.info("Created Company_Handbook.md")

        return created_items


def validate_vault(vault_path: str | Path, auto_fix: bool = False) -> dict:
    """
    Validate vault structure and optionally fix issues.

    Args:
        vault_path: Path to the Obsidian vault root
        auto_fix: Whether to automatically create missing structure

    Returns:
        Dictionary with validation results
    """
    validator = VaultValidator(vault_path)

    # Run structure validation
    is_valid, errors, warnings = validator.validate_structure()

    # Run Plans folder validation
    plans_valid, plans_errors = validator.validate_plans_folder()

    # Get vault statistics
    stats = validator.get_vault_statistics()

    # Auto-fix if requested and validation failed
    created_items = []
    if auto_fix and not is_valid:
        created_items = validator.create_missing_structure()
        # Re-validate after fixes
        is_valid, errors, warnings = validator.validate_structure()

    return {
        'valid': is_valid and plans_valid,
        'structure_valid': is_valid,
        'plans_valid': plans_valid,
        'errors': errors + plans_errors,
        'warnings': warnings,
        'statistics': stats,
        'created_items': created_items
    }

"""
Tests for filesystem watcher core functionality (User Story 1).

Validates that the watcher correctly detects files, creates action items,
prevents duplicates, and handles errors gracefully.
"""

import pytest
import time
from pathlib import Path
from datetime import datetime

from watchers.filesystem_watcher import FilesystemWatcher
from utils.frontmatter_utils import load_action_item
from utils.dedupe_state import DedupeTracker


@pytest.fixture
def test_vault(tmp_path):
    """Create a temporary vault structure for testing."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()

    # Create required folders
    (vault_path / "Needs_Action").mkdir()
    (vault_path / "Done").mkdir()
    (vault_path / "Inbox").mkdir()
    (vault_path / "Plans").mkdir()

    # Create required files
    (vault_path / "Dashboard.md").write_text("# Dashboard\n")
    (vault_path / "Company_Handbook.md").write_text("# Company Handbook\n")

    return vault_path


@pytest.fixture
def test_watch_folder(tmp_path):
    """Create a temporary watch folder for testing."""
    watch_folder = tmp_path / "watch_folder"
    watch_folder.mkdir()
    return watch_folder


@pytest.fixture
def test_dedupe_state(tmp_path):
    """Create a temporary dedupe state file for testing."""
    state_file = tmp_path / "test_dedupe_state.json"
    return state_file


@pytest.fixture
def watcher(test_vault, test_watch_folder, test_dedupe_state):
    """Create a FilesystemWatcher instance for testing."""
    watcher = FilesystemWatcher(
        vault_path=test_vault,
        watch_folder=test_watch_folder,
        watch_mode="polling",
        check_interval=1
    )

    # Override dedupe tracker to use test state file
    watcher.dedupe_tracker = DedupeTracker(test_dedupe_state)

    return watcher


def test_watcher_creates_action_item(watcher, test_watch_folder, test_vault):
    """
    Test that the watcher creates an action item when a file is detected.

    Validates:
    - Action item is created in Needs_Action folder
    - Action item has correct frontmatter
    - Action item references source file
    """
    # Create a test file in watch folder
    test_file = test_watch_folder / "test_document.txt"
    test_file.write_text("This is a test document.")

    # Manually trigger the watcher's file creation handler
    from watchdog.events import FileCreatedEvent
    event = FileCreatedEvent(str(test_file))
    watcher.on_created(event)

    # Verify action item was created
    needs_action = test_vault / "Needs_Action"
    action_items = list(needs_action.glob("*.md"))

    assert len(action_items) == 1, f"Expected 1 action item, found {len(action_items)}"

    # Load and validate the action item
    action_item = load_action_item(action_items[0])

    # Verify required frontmatter fields
    assert action_item['type'] == 'file_drop'
    assert action_item['status'] == 'pending'
    assert 'received' in action_item.metadata
    assert 'source_path' in action_item.metadata
    assert str(test_file) in action_item['source_path']

    # Verify content references the source file
    assert test_file.name in action_item.content
    assert str(test_file.resolve()) in action_item.content


def test_watcher_prevents_duplicates(watcher, test_watch_folder, test_vault):
    """
    Test that the watcher prevents duplicate action items (FR-007).

    Validates:
    - First file creates action item
    - Same file (same path, size, mtime) does not create duplicate
    - Modified file creates new action item
    """
    # Create a test file
    test_file = test_watch_folder / "duplicate_test.txt"
    test_file.write_text("Original content")

    # Trigger watcher for first file
    from watchdog.events import FileCreatedEvent
    event1 = FileCreatedEvent(str(test_file))
    watcher.on_created(event1)

    # Verify first action item was created
    needs_action = test_vault / "Needs_Action"
    action_items_1 = list(needs_action.glob("*.md"))
    assert len(action_items_1) == 1, "First file should create action item"

    # Try to process the same file again (simulate duplicate detection)
    event2 = FileCreatedEvent(str(test_file))
    watcher.on_created(event2)

    # Verify no duplicate was created
    action_items_2 = list(needs_action.glob("*.md"))
    assert len(action_items_2) == 1, "Duplicate file should not create new action item"

    # Modify the file (changes mtime and size)
    time.sleep(0.1)  # Ensure mtime changes
    test_file.write_text("Modified content with different size")

    # Process the modified file
    event3 = FileCreatedEvent(str(test_file))
    watcher.on_created(event3)

    # Verify new action item was created for modified file
    action_items_3 = list(needs_action.glob("*.md"))
    assert len(action_items_3) == 2, "Modified file should create new action item"


def test_watcher_continues_after_error(watcher, test_watch_folder, test_vault, monkeypatch):
    """
    Test that the watcher continues running after encountering errors (FR-008).

    Validates:
    - Error in processing one file doesn't stop the watcher
    - Subsequent files are still processed
    - Errors are logged but don't crash the watcher
    """
    # Create first test file
    test_file_1 = test_watch_folder / "file1.txt"
    test_file_1.write_text("File 1 content")

    # Mock the _create_action_item method to raise an error for the first file
    original_create = watcher._create_action_item
    call_count = [0]

    def mock_create_with_error(file_path):
        call_count[0] += 1
        if call_count[0] == 1:
            # First call raises an error
            raise RuntimeError("Simulated error in action item creation")
        else:
            # Subsequent calls work normally
            return original_create(file_path)

    monkeypatch.setattr(watcher, '_create_action_item', mock_create_with_error)

    # Process first file (should error but not crash)
    from watchdog.events import FileCreatedEvent
    event1 = FileCreatedEvent(str(test_file_1))

    # This should not raise an exception (error is caught and logged)
    try:
        watcher.on_created(event1)
    except Exception as e:
        pytest.fail(f"Watcher should catch errors, but raised: {e}")

    # Verify no action item was created for first file (due to error)
    needs_action = test_vault / "Needs_Action"
    action_items_1 = list(needs_action.glob("*.md"))
    assert len(action_items_1) == 0, "Error should prevent action item creation"

    # Create second test file
    test_file_2 = test_watch_folder / "file2.txt"
    test_file_2.write_text("File 2 content")

    # Process second file (should work normally)
    event2 = FileCreatedEvent(str(test_file_2))
    watcher.on_created(event2)

    # Verify action item was created for second file
    action_items_2 = list(needs_action.glob("*.md"))
    assert len(action_items_2) == 1, "Watcher should continue processing after error"

    # Verify the action item is for file2
    action_item = load_action_item(action_items_2[0])
    assert test_file_2.name in action_item.content


def test_watcher_validates_vault_structure(test_watch_folder, tmp_path):
    """
    Test that the watcher validates vault structure on initialization.

    Validates:
    - Watcher raises error if vault structure is invalid
    - Watcher initializes successfully with valid vault structure
    """
    # Create invalid vault (missing required folders)
    invalid_vault = tmp_path / "invalid_vault"
    invalid_vault.mkdir()

    # Try to create watcher with invalid vault
    with pytest.raises(ValueError, match="Invalid vault structure"):
        FilesystemWatcher(
            vault_path=invalid_vault,
            watch_folder=test_watch_folder,
            watch_mode="polling"
        )

    # Create valid vault structure
    valid_vault = tmp_path / "valid_vault"
    valid_vault.mkdir()
    (valid_vault / "Needs_Action").mkdir()
    (valid_vault / "Done").mkdir()
    (valid_vault / "Dashboard.md").write_text("# Dashboard")
    (valid_vault / "Company_Handbook.md").write_text("# Handbook")

    # Watcher should initialize successfully
    watcher = FilesystemWatcher(
        vault_path=valid_vault,
        watch_folder=test_watch_folder,
        watch_mode="polling"
    )

    assert watcher.vault_path == valid_vault
    assert watcher.needs_action == valid_vault / "Needs_Action"


def test_watcher_ignores_directories(watcher, test_watch_folder, test_vault):
    """
    Test that the watcher ignores directory creation events.

    Only files should trigger action item creation.
    """
    # Create a directory in watch folder
    test_dir = test_watch_folder / "test_directory"
    test_dir.mkdir()

    # Trigger watcher with directory event
    from watchdog.events import DirCreatedEvent
    event = DirCreatedEvent(str(test_dir))
    watcher.on_created(event)

    # Verify no action item was created
    needs_action = test_vault / "Needs_Action"
    action_items = list(needs_action.glob("*.md"))
    assert len(action_items) == 0, "Directory creation should not create action item"


def test_watcher_generates_stable_ids(watcher, test_watch_folder):
    """
    Test that the watcher generates stable IDs for files.

    Same file should always generate the same ID.
    """
    # Create a test file
    test_file = test_watch_folder / "stable_id_test.txt"
    test_file.write_text("Test content")

    # Generate ID multiple times
    id1 = watcher._generate_stable_id(test_file)
    id2 = watcher._generate_stable_id(test_file)

    # IDs should be identical
    assert id1 == id2, "Same file should generate same ID"

    # Modify file
    time.sleep(0.1)
    test_file.write_text("Modified content")

    # Generate ID for modified file
    id3 = watcher._generate_stable_id(test_file)

    # ID should be different after modification
    assert id3 != id1, "Modified file should generate different ID"


def test_watcher_check_for_updates(watcher, test_watch_folder):
    """
    Test the check_for_updates method for polling mode.

    Validates:
    - Method returns list of new files
    - Already processed files are not returned
    """
    # Create test files
    file1 = test_watch_folder / "file1.txt"
    file2 = test_watch_folder / "file2.txt"
    file1.write_text("File 1")
    file2.write_text("File 2")

    # Check for updates (should find both files)
    new_files = watcher.check_for_updates()
    assert len(new_files) == 2, "Should find both new files"

    # Mark file1 as processed
    file1_id = watcher._generate_stable_id(file1)
    watcher.dedupe_tracker.mark_processed(file1_id)

    # Check for updates again (should only find file2)
    new_files = watcher.check_for_updates()
    assert len(new_files) == 1, "Should only find unprocessed file"
    assert new_files[0] == file2, "Should return file2"

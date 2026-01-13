"""Tests for filesystem watcher core functionality.

Validates watcher behavior, deduplication logic, and error resilience.
"""

import tempfile
import time
from pathlib import Path

import pytest

from My_AI_Employee.src.my_ai_employee.utils import DedupeTracker, load_action_item
from My_AI_Employee.src.my_ai_employee.watchers.filesystem_watcher import (
    FilesystemWatcher,
)


@pytest.fixture
def temp_vault():
    """Create a temporary vault structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "vault"
        vault_path.mkdir()

        # Create required folders
        (vault_path / "Inbox").mkdir()
        (vault_path / "Needs_Action").mkdir()
        (vault_path / "Done").mkdir()
        (vault_path / "Dashboard.md").write_text("# Dashboard")
        (vault_path / "Company_Handbook.md").write_text("# Handbook")

        yield vault_path


@pytest.fixture
def temp_watch_folder():
    """Create a temporary watch folder for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        watch_path = Path(tmpdir) / "watch"
        watch_path.mkdir()
        yield watch_path


@pytest.fixture
def temp_dedupe_file():
    """Create a temporary dedupe state file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dedupe_path = Path(tmpdir) / "dedupe.json"
        yield dedupe_path


def test_watcher_creates_action_item(
    temp_vault, temp_watch_folder, temp_dedupe_file
):
    """Test that watcher creates action items for dropped files.

    This validates the core US1 functionality: file drop → action item.
    """
    # Create watcher instance
    watcher = FilesystemWatcher(
        vault_path=temp_vault,
        watch_folder=temp_watch_folder,
        watch_mode="events",
        dedupe_state_file=temp_dedupe_file,
    )

    # Count initial action items
    needs_action = temp_vault / "Needs_Action"
    initial_count = len(list(needs_action.glob("*.md")))

    # Simulate file drop by creating a file
    test_file = temp_watch_folder / "test_document.txt"
    test_file.write_text("Test content")

    # Manually trigger the on_created handler (simulating watchdog event)
    from watchdog.events import FileCreatedEvent

    event = FileCreatedEvent(str(test_file))
    watcher.on_created(event)

    # Verify action item was created
    final_count = len(list(needs_action.glob("*.md")))
    assert final_count == initial_count + 1

    # Verify the action item has correct structure
    action_items = list(needs_action.glob("*.md"))
    latest_item = sorted(action_items, key=lambda p: p.stat().st_mtime)[-1]

    # Load and verify frontmatter
    post = load_action_item(latest_item)
    assert post["type"] == "file_drop"
    assert post["status"] == "pending"
    assert "received" in post.metadata
    assert str(test_file.absolute()) in post.content


def test_watcher_prevents_duplicates(
    temp_vault, temp_watch_folder, temp_dedupe_file
):
    """Test that watcher prevents duplicate action items.

    Per FR-007: Must prevent duplicate processing.
    """
    # Create watcher instance
    watcher = FilesystemWatcher(
        vault_path=temp_vault,
        watch_folder=temp_watch_folder,
        watch_mode="events",
        dedupe_state_file=temp_dedupe_file,
    )

    # Create a test file
    test_file = temp_watch_folder / "duplicate_test.txt"
    test_file.write_text("Test content")

    needs_action = temp_vault / "Needs_Action"

    # First drop - should create action item
    from watchdog.events import FileCreatedEvent

    event = FileCreatedEvent(str(test_file))
    watcher.on_created(event)

    first_count = len(list(needs_action.glob("*.md")))
    assert first_count >= 1

    # Second drop of same file - should NOT create another action item
    watcher.on_created(event)

    second_count = len(list(needs_action.glob("*.md")))
    assert second_count == first_count, "Duplicate file created extra action item"

    # Verify dedupe tracker registered the file
    stable_id = watcher._generate_stable_id(test_file)
    assert watcher.dedupe_tracker.is_processed(stable_id)


def test_watcher_continues_after_error(
    temp_vault, temp_watch_folder, temp_dedupe_file
):
    """Test that watcher continues running after errors.

    Per FR-008: Must log errors and continue running.
    """
    # Create watcher instance
    watcher = FilesystemWatcher(
        vault_path=temp_vault,
        watch_folder=temp_watch_folder,
        watch_mode="events",
        dedupe_state_file=temp_dedupe_file,
    )

    needs_action = temp_vault / "Needs_Action"

    # Create a file that will cause an error (e.g., deleted before processing)
    test_file1 = temp_watch_folder / "error_test.txt"
    test_file1.write_text("Will cause error")

    from watchdog.events import FileCreatedEvent

    # Simulate event for deleted file (will cause stat error)
    test_file1.unlink()  # Delete file before processing
    event1 = FileCreatedEvent(str(test_file1))

    # This should log an error but not crash
    try:
        watcher.on_created(event1)
    except Exception as e:
        pytest.fail(f"Watcher crashed on error: {e}")

    # Create a valid file to verify watcher still works
    test_file2 = temp_watch_folder / "valid_test.txt"
    test_file2.write_text("Valid content")

    event2 = FileCreatedEvent(str(test_file2))
    watcher.on_created(event2)

    # Verify the valid file created an action item
    action_items = list(needs_action.glob("*.md"))
    assert len(action_items) >= 1

    # Verify the action item is for the valid file
    found_valid = False
    for item in action_items:
        post = load_action_item(item)
        if "valid_test.txt" in post.content:
            found_valid = True
            break

    assert found_valid, "Watcher did not process valid file after error"


def test_watcher_ignores_temporary_files(
    temp_vault, temp_watch_folder, temp_dedupe_file
):
    """Test that watcher ignores temporary and hidden files."""
    watcher = FilesystemWatcher(
        vault_path=temp_vault,
        watch_folder=temp_watch_folder,
        watch_mode="events",
        dedupe_state_file=temp_dedupe_file,
    )

    needs_action = temp_vault / "Needs_Action"
    initial_count = len(list(needs_action.glob("*.md")))

    from watchdog.events import FileCreatedEvent

    # Test hidden file (starts with .)
    hidden_file = temp_watch_folder / ".hidden_file"
    hidden_file.write_text("Hidden")
    watcher.on_created(FileCreatedEvent(str(hidden_file)))

    # Test temporary file patterns
    temp_patterns = [".tmp", ".temp", ".swp", ".swo", "~"]
    for pattern in temp_patterns:
        temp_file = temp_watch_folder / f"file{pattern}"
        temp_file.write_text("Temp")
        watcher.on_created(FileCreatedEvent(str(temp_file)))

    # Verify no action items were created
    final_count = len(list(needs_action.glob("*.md")))
    assert (
        final_count == initial_count
    ), "Temporary files created action items"


def test_dedupe_tracker_functionality(temp_dedupe_file):
    """Test DedupeTracker class operations."""
    tracker = DedupeTracker(temp_dedupe_file)

    # Initially empty
    assert tracker.count() == 0

    # Mark items as processed
    tracker.mark_processed("id1")
    tracker.mark_processed("id2")

    assert tracker.count() == 2
    assert tracker.is_processed("id1")
    assert tracker.is_processed("id2")
    assert not tracker.is_processed("id3")

    # Verify persistence
    tracker2 = DedupeTracker(temp_dedupe_file)
    assert tracker2.count() == 2
    assert tracker2.is_processed("id1")
    assert tracker2.is_processed("id2")

    # Test clear
    tracker2.clear()
    assert tracker2.count() == 0
    assert not tracker2.is_processed("id1")


def test_watcher_stable_id_generation(temp_vault, temp_watch_folder, temp_dedupe_file):
    """Test that stable IDs are generated consistently."""
    watcher = FilesystemWatcher(
        vault_path=temp_vault,
        watch_folder=temp_watch_folder,
        watch_mode="events",
        dedupe_state_file=temp_dedupe_file,
    )

    # Create a test file
    test_file = temp_watch_folder / "stable_id_test.txt"
    test_file.write_text("Content for stable ID test")

    # Generate ID multiple times
    id1 = watcher._generate_stable_id(test_file)
    id2 = watcher._generate_stable_id(test_file)

    # IDs should be identical for same file
    assert id1 == id2
    assert isinstance(id1, str)
    assert len(id1) == 64  # SHA256 hash length

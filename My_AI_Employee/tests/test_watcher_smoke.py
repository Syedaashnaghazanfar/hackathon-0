"""Smoke test for the filesystem watcher.

This script:
1. Starts the watcher in a separate process
2. Creates a test file in the watch folder
3. Verifies an action item appears in Needs_Action/
4. Cleans up and reports results
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def count_action_items(vault_path: Path) -> int:
    """Count markdown files in Needs_Action folder."""
    needs_action = vault_path / "Needs_Action"
    if not needs_action.exists():
        return 0
    return len(list(needs_action.glob("*.md")))


def main() -> int:
    """Run the smoke test."""
    print("=" * 60)
    print("Filesystem Watcher Smoke Test")
    print("=" * 60)

    # Setup paths
    vault_path = Path("AI_Employee_Vault").resolve()
    watch_folder = Path("watch_folder").resolve()

    print(f"Vault: {vault_path}")
    print(f"Watch Folder: {watch_folder}")
    print()

    # Count initial action items
    initial_count = count_action_items(vault_path)
    print(f"Initial action items: {initial_count}")

    # Start watcher in background
    print("\nStarting watcher...")
    watcher_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "my_ai_employee.run_watcher",
            "--vault-path",
            str(vault_path),
            "--watch-folder",
            str(watch_folder),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give watcher time to initialize
    print("Waiting 3 seconds for watcher to initialize...")
    time.sleep(3)

    # Check if watcher is still running
    if watcher_process.poll() is not None:
        stdout, stderr = watcher_process.communicate()
        print("\n[FAIL] Watcher failed to start!")
        print("\nSTDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        return 1

    print("[OK] Watcher started successfully")

    try:
        # Create test file
        test_file = watch_folder / "test_document.txt"
        print(f"\nCreating test file: {test_file}")
        test_file.write_text("This is a test file for the watcher smoke test.\n")
        print("[OK] Test file created")

        # Wait for watcher to process
        print("\nWaiting 5 seconds for watcher to process file...")
        time.sleep(5)

        # Count action items again
        final_count = count_action_items(vault_path)
        print(f"Final action items: {final_count}")

        # Verify action item was created
        if final_count > initial_count:
            print("\n[SUCCESS] SUCCESS: Action item created!")
            print(f"   New items: {final_count - initial_count}")

            # Show the new action item(s)
            needs_action = vault_path / "Needs_Action"
            items = sorted(needs_action.glob("*.md"), key=lambda p: p.stat().st_mtime)
            if items:
                latest = items[-1]
                print(f"   Latest item: {latest.name}")
                print(f"\n   Content preview:")
                content = latest.read_text()
                print("   " + "\n   ".join(content.split("\n")[:10]))

            return 0
        else:
            print("\n[FAIL] FAILURE: No action item created!")
            print("   Check watcher logs below:")
            return 1

    finally:
        # Stop watcher
        print("\n\nStopping watcher...")
        watcher_process.terminate()
        try:
            watcher_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            watcher_process.kill()

        # Get watcher output
        stdout, stderr = watcher_process.communicate()
        print("\n" + "=" * 60)
        print("Watcher Output:")
        print("=" * 60)
        if stdout:
            print(stdout)
        if stderr:
            print("\nErrors:")
            print(stderr)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Orchestrator - Automation Glue for Silver Tier AI Employee

This is the "Master Process" that watches folders and triggers Claude Code
to process files. It does NOT execute actions directly - it triggers Claude,
and Claude uses MCP tools to execute actions.

Architecture:
    Orchestrator (this file) → Watches folders, triggers Claude
    Claude Code → Reads files, uses MCP tools
    MCP Servers → Execute actions (email, LinkedIn, browser)

Jobs:
    1. Scheduling - Handle timing (check every N seconds)
    2. Folder Watching - Monitor Needs_Action, Approved, Pending_Approval
    3. Process Management - Keep watchers alive
    4. Trigger Claude - Call Claude Code via subprocess when files appear
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
VAULT_ROOT = os.getenv('VAULT_ROOT', 'AI_Employee_Vault')
CHECK_INTERVAL = int(os.getenv('ORCHESTRATOR_CHECK_INTERVAL', '10'))

# Setup logging
log_file = Path(VAULT_ROOT) / 'Logs' / 'orchestrator.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Orchestrator')


class Orchestrator:
    """
    Orchestrator - Automation Glue

    Watches folders and triggers Claude Code to process files.
    Does NOT execute actions directly.
    """

    def __init__(self):
        self.vault_root = Path(VAULT_ROOT)
        self.needs_action_dir = self.vault_root / 'Needs_Action'
        self.approved_dir = self.vault_root / 'Approved'
        self.pending_approval_dir = self.vault_root / 'Pending_Approval'
        self.done_dir = self.vault_root / 'Done'

        self.running = False

        # Track processed files to avoid re-processing
        self.processed_needs_action = set()
        self.processed_approved = set()

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [self.needs_action_dir, self.approved_dir,
                         self.pending_approval_dir, self.done_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def start(self):
        """Start the orchestrator main loop."""
        logger.info("=" * 60)
        logger.info("Starting Orchestrator (Automation Glue)")
        logger.info("=" * 60)
        logger.info(f"Vault root: {self.vault_root}")
        logger.info(f"Check interval: {CHECK_INTERVAL}s")
        logger.info("")
        logger.info("Orchestrator watches folders and triggers Claude Code.")
        logger.info("Claude Code uses MCP tools to execute actions.")
        logger.info("")

        self.running = True

        try:
            while self.running:
                try:
                    # Check for new items in Needs_Action
                    self._check_needs_action()

                    # Check for approved items ready for execution
                    self._check_approved()

                    # Sleep until next check
                    time.sleep(CHECK_INTERVAL)

                except Exception as e:
                    logger.error(f"Error in orchestrator loop: {e}")
                    time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            self.stop()

    def stop(self):
        """Stop the orchestrator."""
        self.running = False
        logger.info("Orchestrator stopped")

    def _check_needs_action(self):
        """
        Check Needs_Action folder for new files.

        When files are found, trigger Claude Code to process them
        using the /needs-action-triage skill.
        """
        if not self.needs_action_dir.exists():
            return

        files = list(self.needs_action_dir.glob('*.md'))
        new_files = [f for f in files if f.name not in self.processed_needs_action]

        if new_files:
            logger.info(f"Found {len(new_files)} new items in Needs_Action/")

            for file_path in new_files:
                logger.info(f"  - {file_path.name}")

                # Trigger Claude Code to process this file
                self._trigger_claude_for_needs_action(file_path)

                # Mark as processed
                self.processed_needs_action.add(file_path.name)

    def _check_approved(self):
        """
        Check Approved folder for files ready for execution.

        When files are found, trigger Claude Code to execute them
        using MCP tools.
        """
        if not self.approved_dir.exists():
            return

        files = list(self.approved_dir.glob('*.md'))
        new_files = [f for f in files if f.name not in self.processed_approved]

        if new_files:
            logger.info(f"Found {len(new_files)} approved items ready for execution")

            for file_path in new_files:
                logger.info(f"  - {file_path.name}")

                # Trigger Claude Code to execute this approved action
                self._trigger_claude_for_approved(file_path)

                # Mark as processed
                self.processed_approved.add(file_path.name)

    def _trigger_claude_for_needs_action(self, file_path: Path):
        """
        Trigger Claude Code to process a Needs_Action item.

        Claude will use the /needs-action-triage skill to:
        - Read the action item
        - Create a plan
        - Generate approval request if needed
        - Update dashboard
        """
        logger.info(f"Triggering Claude Code to process: {file_path.name}")

        prompt = f"""Process the action item in {file_path}.

Use the /needs-action-triage skill to:
1. Read the action item
2. Analyze it according to Company_Handbook.md rules
3. Create a plan in Plans/ folder
4. If external action is needed, create approval request in Pending_Approval/
5. Update Dashboard.md
6. Move processed item to Done/

The file has been detected by a watcher and needs processing."""

        try:
            # Call Claude Code via subprocess
            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                logger.info(f"✅ Claude processed {file_path.name} successfully")
            else:
                logger.error(f"❌ Claude failed to process {file_path.name}")
                logger.error(f"Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ Claude timed out processing {file_path.name}")
        except FileNotFoundError:
            logger.error("❌ 'claude' command not found. Is Claude Code installed?")
        except Exception as e:
            logger.error(f"❌ Error triggering Claude: {e}")

    def _trigger_claude_for_approved(self, file_path: Path):
        """
        Trigger Claude Code to execute an approved action.

        Claude will:
        - Read the approved action file
        - Use the appropriate MCP tool (email_mcp, linkedin_mcp, etc.)
        - Execute the action
        - Move the file to Done/ with results
        """
        logger.info(f"Triggering Claude Code to execute: {file_path.name}")

        prompt = f"""Execute the approved action in {file_path}.

This file has been approved by a human and is ready for execution.

Steps:
1. Read the file to understand the action
2. Use the appropriate MCP tool to execute:
   - For email: Use email_mcp send_email tool
   - For LinkedIn: Use linkedin_mcp tool
   - For browser: Use browser_mcp tool
3. Capture the result
4. Create execution record in Done/ with results
5. **IMPORTANT**: Read the 'original_file' field from the approval's frontmatter
6. **IMPORTANT**: Move the original file from Needs_Action/ to Done/ with execution metadata
7. Update Dashboard.md

The action has been approved and should be executed now.

CRITICAL: After successful execution, you MUST move the original action item file from Needs_Action/ to Done/. The original file path is specified in the approval's 'original_file' field."""

        try:
            # Call Claude Code via subprocess
            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.returncode == 0:
                logger.info(f"✅ Claude executed {file_path.name} successfully")
            else:
                logger.error(f"❌ Claude failed to execute {file_path.name}")
                logger.error(f"Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ Claude timed out executing {file_path.name}")
        except FileNotFoundError:
            logger.error("❌ 'claude' command not found. Is Claude Code installed?")
        except Exception as e:
            logger.error(f"❌ Error triggering Claude: {e}")


def main():
    """Main entry point."""
    orchestrator = Orchestrator()

    try:
        orchestrator.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
Orchestrator for Silver Tier AI Employee.

Watches /Approved/ folder and routes actions to appropriate MCP servers.
"""

import time
import logging
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import frontmatter

from my_ai_employee.config import get_config
from my_ai_employee.utils.audit_logger import AuditLogger
from my_ai_employee.utils.sanitizer import sanitize_tool_inputs, sanitize_error_message
from my_ai_employee.utils import log_heartbeat
from my_ai_employee.vault_ops.dashboard_updater import DashboardUpdater


logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrator for executing approved actions.

    Watches /Approved/ folder, routes actions to MCP servers, handles retries,
    and moves completed/failed actions to /Done/ or /Failed/ folders.
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize orchestrator.

        Args:
            vault_path: Path to vault root (defaults to config.vault_root)
        """
        if vault_path is None:
            config = get_config()
            vault_path = config.vault_root

        self.vault_path = vault_path
        self.approved_dir = vault_path / "Approved"
        self.done_dir = vault_path / "Done"
        self.failed_dir = vault_path / "Failed"
        self.config = get_config()
        self.audit_logger = AuditLogger(vault_path)
        self.dashboard_updater = DashboardUpdater(vault_path)
        self.running = False
        self.start_time = datetime.now()
        self.actions_processed = 0
        self.successful_actions = 0
        self.failed_actions = 0

        # Ensure directories exist
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        logger.info(f"Orchestrator initialized, watching: {self.approved_dir}")

    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.stop()

    def run(self, check_interval: int = 10) -> None:
        """
        Run orchestrator loop.

        Args:
            check_interval: Seconds between checks (default: 10)
        """
        self.running = True
        logger.info(f"Orchestrator started, checking every {check_interval}s")

        while self.running:
            try:
                # Log heartbeat every 60 seconds
                if int((datetime.now() - self.start_time).total_seconds()) % 60 < check_interval:
                    log_heartbeat(logger, "orchestrator")

                self._process_approved_actions()
                time.sleep(check_interval)
            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Orchestrator error: {e}", exc_info=True)
                time.sleep(check_interval)

    def stop(self) -> None:
        """Stop orchestrator loop."""
        self.running = False
        logger.info("Orchestrator stopping...")

    def _process_approved_actions(self) -> None:
        """
        Process all approved actions in /Approved/ folder.
        """
        approved_files = list(self.approved_dir.glob("*-approved.md"))

        if not approved_files:
            return

        logger.info(f"Found {len(approved_files)} approved action(s) to process")

        for approved_file in approved_files:
            try:
                self._execute_action(approved_file)
            except Exception as e:
                logger.error(f"Failed to execute action {approved_file.name}: {e}", exc_info=True)

    def _execute_action(self, approved_file: Path) -> None:
        """
        Execute a single approved action.

        Args:
            approved_file: Path to approved action file
        """
        # Read approved action file
        with open(approved_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        action_id = post.metadata.get("action_id")
        action_type = post.metadata.get("action_type")

        logger.info(f"Executing action {action_id} (type: {action_type})")

        # Extract execution plan from content
        execution_plan = self._parse_execution_plan(post.content)

        if not execution_plan:
            logger.error(f"No execution plan found in {approved_file.name}")
            self._move_to_failed(approved_file, "No execution plan found")
            return

        # Route to appropriate MCP server with retry logic
        result = self._execute_with_retry(
            action_type=action_type,
            execution_plan=execution_plan,
            max_retries=3,
        )

        # Log execution to audit trail
        self._log_execution(
            action_id=action_id,
            action_type=action_type,
            execution_plan=execution_plan,
            result=result,
        )

        # Handle result
        if result.get("status") in ["success", "dry_run"]:
            self._move_to_done(approved_file, result)
            logger.info(f"Action {action_id} completed successfully")
            self.actions_processed += 1
            self.successful_actions += 1

            # Update dashboard
            self.dashboard_updater.add_recent_activity(
                action_id=action_id,
                action_type=action_type,
                status="success" if result.get("status") == "success" else "dry_run",
                description=f"Executed via {execution_plan.get('mcp_server', 'unknown')} MCP server"
            )
            self.dashboard_updater.update_pending_count()
        else:
            self._move_to_failed(approved_file, result.get("error_message", "Unknown error"))
            logger.error(f"Action {action_id} failed: {result.get('error_message')}")
            self.actions_processed += 1
            self.failed_actions += 1

            # Update dashboard
            self.dashboard_updater.add_recent_activity(
                action_id=action_id,
                action_type=action_type,
                status="failed",
                description=f"Error: {result.get('error_message', 'Unknown error')[:100]}"
            )
            self.dashboard_updater.update_pending_count()

    def _parse_execution_plan(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse execution plan from approval request content.

        Args:
            content: Approval request markdown content

        Returns:
            Execution plan dictionary or None
        """
        # Extract YAML code block containing execution plan
        import re
        import yaml

        pattern = r"```yaml\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            return None

        # Find execution_plan section
        for match in matches:
            try:
                data = yaml.safe_load(match)
                if isinstance(data, dict) and "mcp_server" in data:
                    return data
                elif isinstance(data, dict) and "execution_plan" in data:
                    return data["execution_plan"]
            except yaml.YAMLError:
                continue

        return None

    def _execute_with_retry(
        self,
        action_type: str,
        execution_plan: Dict[str, Any],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute action with exponential backoff retry.

        Args:
            action_type: Type of action
            execution_plan: Execution plan with MCP server and tool details
            max_retries: Maximum number of retries

        Returns:
            Execution result dictionary
        """
        mcp_server = execution_plan.get("mcp_server")
        tool_inputs = execution_plan.get("tool_inputs", {})
        backoff_seconds = [1, 2, 4]

        for attempt in range(max_retries):
            try:
                result = self._route_to_mcp_server(mcp_server, action_type, tool_inputs)

                # Check if retry needed
                if result.get("status") == "error":
                    error_type = result.get("error_type")

                    # Retry on rate limit or transient errors
                    if error_type in ["rate_limit_exceeded", "timeout", "network_error"]:
                        if attempt < max_retries - 1:
                            wait_time = backoff_seconds[min(attempt, len(backoff_seconds) - 1)]
                            logger.warning(
                                f"Transient error, retrying in {wait_time}s "
                                f"(attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                            continue

                # Success or non-retryable error
                result["retry_count"] = attempt
                return result

            except Exception as e:
                logger.error(f"Execution attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = backoff_seconds[min(attempt, len(backoff_seconds) - 1)]
                    time.sleep(wait_time)
                else:
                    return {
                        "status": "error",
                        "error_type": "unknown_error",
                        "error_message": str(e),
                        "retry_count": attempt,
                    }

        return {
            "status": "error",
            "error_type": "max_retries_exceeded",
            "error_message": f"Failed after {max_retries} attempts",
            "retry_count": max_retries,
        }

    def _route_to_mcp_server(
        self,
        mcp_server: str,
        action_type: str,
        tool_inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Route action to appropriate MCP server.

        Args:
            mcp_server: MCP server name (email, linkedin, browser)
            action_type: Action type
            tool_inputs: Tool input parameters

        Returns:
            Execution result dictionary
        """
        # Handle dry-run mode at orchestrator level
        if self.config.dry_run:
            logger.info("[DRY RUN] Would execute action:")
            logger.info(f"  MCP Server: {mcp_server}")
            logger.info(f"  Action Type: {action_type}")
            logger.info(f"  Tool Inputs: {sanitize_tool_inputs(tool_inputs)}")

            return {
                "status": "dry_run",
                "message": f"Dry-run mode: {action_type} not actually executed",
                "mcp_server": mcp_server,
                "action_type": action_type,
            }

        # In production mode, would call actual MCP servers here
        # For now, return dry_run response since MCP servers aren't callable directly
        logger.warning("Production mode MCP execution not yet implemented")
        logger.info(f"Would call {mcp_server} MCP server with action: {action_type}")

        return {
            "status": "dry_run",
            "message": f"MCP execution placeholder: {action_type}",
            "mcp_server": mcp_server,
            "action_type": action_type,
        }

    def _log_execution(
        self,
        action_id: str,
        action_type: str,
        execution_plan: Dict[str, Any],
        result: Dict[str, Any],
    ) -> None:
        """
        Log execution to audit trail.

        Args:
            action_id: Action ID
            action_type: Action type
            execution_plan: Execution plan
            result: Execution result
        """
        # Sanitize tool inputs
        tool_inputs_sanitized = sanitize_tool_inputs(execution_plan.get("tool_inputs", {}))

        # Sanitize error message if present
        error_message = result.get("error_message")
        if error_message:
            error_message = sanitize_error_message(error_message)

        # Log to audit trail
        self.audit_logger.log_execution(
            action_type=action_type,
            execution_status=result.get("status", "unknown"),
            executor="ai_employee",
            executor_id="orchestrator",
            tool_name=execution_plan.get("tool_name", action_type),
            tool_inputs_sanitized=tool_inputs_sanitized,
            mcp_server=execution_plan.get("mcp_server", "unknown"),
            error=error_message,
            retry_count=result.get("retry_count", 0),
        )

    def _move_to_done(self, approved_file: Path, result: Dict[str, Any]) -> None:
        """
        Move approved action to /Done/ folder with execution result.

        Args:
            approved_file: Path to approved action file
            result: Execution result
        """
        # Read file
        with open(approved_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Update metadata
        post.metadata["status"] = "completed"
        post.metadata["executed_at"] = datetime.now().isoformat()
        post.metadata["execution_status"] = result.get("status")

        # Append execution result to content
        post.content += f"\n\n---\n\n## Execution Result\n\n"
        post.content += f"**Status**: {result.get('status')}\n"
        post.content += f"**Executed at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        if result.get("message_id"):
            post.content += f"**Message ID**: {result.get('message_id')}\n"
        if result.get("post_id"):
            post.content += f"**Post ID**: {result.get('post_id')}\n"
        if result.get("retry_count", 0) > 0:
            post.content += f"**Retry Count**: {result.get('retry_count')}\n"

        # Write to Done folder
        done_file = self.done_dir / approved_file.name.replace("-approved", "-completed")
        with open(done_file, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        # Remove from Approved folder
        approved_file.unlink()

        logger.info(f"Moved to Done: {done_file.name}")

    def _move_to_failed(self, approved_file: Path, error_message: str) -> None:
        """
        Move approved action to /Failed/ folder with error details.

        Args:
            approved_file: Path to approved action file
            error_message: Error message
        """
        # Read file
        with open(approved_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Update metadata
        post.metadata["status"] = "failed"
        post.metadata["failed_at"] = datetime.now().isoformat()
        post.metadata["error_message"] = sanitize_error_message(error_message)

        # Append failure details to content
        post.content += f"\n\n---\n\n## Execution Failed\n\n"
        post.content += f"**Status**: Failed\n"
        post.content += f"**Failed at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        post.content += f"**Error**: {sanitize_error_message(error_message)}\n"

        # Write to Failed folder
        failed_file = self.failed_dir / approved_file.name.replace("-approved", "-failed")
        with open(failed_file, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        # Remove from Approved folder
        approved_file.unlink()

        logger.warning(f"Moved to Failed: {failed_file.name}")


def main():
    """
    Main entry point for orchestrator.
    """
    import logging

    # Setup basic logging to console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    config = get_config()

    # Print startup banner
    print("=" * 60)
    print("Silver AI Employee - Orchestrator")
    print("=" * 60)
    print(f"Vault Path: {config.vault_root}")
    print(f"Check Interval: 10s")
    print(f"DRY_RUN mode: {config.dry_run}")
    print("=" * 60)
    print()

    # Create and run orchestrator
    orchestrator = Orchestrator()

    try:
        orchestrator.run(check_interval=10)
    except KeyboardInterrupt:
        logger.info("\nOrchestrator stopped by user")
        orchestrator.stop()


if __name__ == "__main__":
    main()

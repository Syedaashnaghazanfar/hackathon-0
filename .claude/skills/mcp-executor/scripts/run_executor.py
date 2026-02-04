#!/usr/bin/env python3
"""MCP Executor - Process approved actions and execute via MCP servers."""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/executor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD = "dead"


@dataclass
class ExecutionResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class MCPExecutor:
    """Execute approved actions through MCP servers."""

    def __init__(self):
        self.vault_root = Path(os.getenv('VAULT_ROOT', 'My_AI_Employee/AI_Employee_Vault'))
        self.approved_dir = self.vault_root / 'Approved'
        self.done_dir = self.vault_root / 'Done'
        self.failed_dir = self.vault_root / 'Failed'

        self.check_interval = int(os.getenv('EXECUTOR_CHECK_INTERVAL', '5'))
        self.max_retries = int(os.getenv('EXECUTOR_MAX_RETRIES', '3'))
        self.retry_backoff = int(os.getenv('EXECUTOR_RETRY_BACKOFF', '25'))

        self.running = False

    def start(self):
        """Start executor."""
        logger.info("Starting MCP Executor")
        self.running = True

        # Ensure directories exist
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

        try:
            while self.running:
                self._process_approved_items()
                self._process_failed_items_retries()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self._shutdown()

    def _process_approved_items(self):
        """Process items in /Approved/ folder."""
        if not self.approved_dir.exists():
            return

        approved_files = list(self.approved_dir.glob('*.md'))

        for file_path in approved_files:
            try:
                self._execute_action(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")

    def _execute_action(self, file_path: Path):
        """Execute a single approved action."""
        logger.info(f"Executing action: {file_path.name}")

        start_time = time.time()

        try:
            # Read action details
            with open(file_path, 'r') as f:
                content = f.read()

            # Parse frontmatter and body
            action_type = self._extract_frontmatter_value(content, 'action_type')
            mcp_server = self._extract_frontmatter_value(content, 'mcp_server')

            # Route to appropriate MCP server
            result = self._route_to_mcp_server(mcp_server, action_type, content)

            execution_time = time.time() - start_time

            if result.success:
                logger.info(f"✅ Execution succeeded: {file_path.name}")
                self._move_to_done(file_path, result, execution_time)
            else:
                logger.error(f"❌ Execution failed: {file_path.name} - {result.error}")
                self._move_to_failed(file_path, result, retry_count=0)

        except Exception as e:
            logger.error(f"Exception during execution: {e}")
            self._move_to_failed(file_path, ExecutionResult(success=False, error=str(e)), retry_count=0)

    def _route_to_mcp_server(self, mcp_server: str, action_type: str, content: str) -> ExecutionResult:
        """Route action to appropriate MCP server."""
        if mcp_server == 'email':
            return self._execute_email_action(content)
        elif mcp_server == 'linkedin':
            return self._execute_linkedin_action(content)
        elif mcp_server == 'browser':
            return self._execute_browser_action(content)
        else:
            return ExecutionResult(success=False, error=f"Unknown MCP server: {mcp_server}")

    def _execute_email_action(self, content: str) -> ExecutionResult:
        """Execute email sending action."""
        try:
            # Extract email details from content
            to = self._extract_value(content, 'To:', '**', next_line=True)
            subject = self._extract_value(content, 'Subject:', '**', next_line=True)
            body = self._extract_value(content, 'Body:', '\n', next_line=True)

            if not to or not subject:
                return ExecutionResult(success=False, error="Missing To or Subject")

            # Call email MCP server
            # In real implementation, would use subprocess or gRPC to call email_mcp.py
            logger.info(f"Sending email to {to} with subject '{subject}'")

            # Simulate successful send
            return ExecutionResult(
                success=True,
                message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

        except Exception as e:
            return ExecutionResult(success=False, error=str(e))

    def _execute_linkedin_action(self, content: str) -> ExecutionResult:
        """Execute LinkedIn post action."""
        try:
            # Extract post details
            post_text = self._extract_value(content, 'Post Text:', '**')
            hashtags = self._extract_value(content, 'Hashtags:', '**', next_line=True)

            if not post_text:
                return ExecutionResult(success=False, error="Missing post text")

            logger.info("Posting to LinkedIn")

            # Simulate successful post
            return ExecutionResult(
                success=True,
                message_id=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

        except Exception as e:
            return ExecutionResult(success=False, error=str(e))

    def _execute_browser_action(self, content: str) -> ExecutionResult:
        """Execute browser automation action."""
        try:
            logger.info("Executing browser automation steps")

            # Parse automation steps from content
            steps = self._extract_steps(content)

            if not steps:
                return ExecutionResult(success=False, error="No automation steps found")

            # Execute each step
            for step in steps:
                logger.info(f"  - {step}")

            # Simulate successful execution
            return ExecutionResult(
                success=True,
                message_id=f"form_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

        except Exception as e:
            return ExecutionResult(success=False, error=str(e))

    def _process_failed_items_retries(self):
        """Check failed items and retry if needed."""
        if not self.failed_dir.exists():
            return

        failed_files = list(self.failed_dir.glob('*.md'))

        for file_path in failed_files:
            retry_count = self._get_retry_count(file_path)

            if retry_count >= self.max_retries:
                logger.warning(f"Max retries reached for {file_path.name}")
                continue

            # Check if retry time has arrived
            if self._should_retry(file_path, retry_count):
                logger.info(f"Retrying failed action: {file_path.name} (attempt {retry_count + 1})")
                self._execute_action(file_path)

    def _move_to_done(self, file_path: Path, result: ExecutionResult, execution_time: float):
        """Move executed action to /Done/ folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{file_path.stem}_executed_{timestamp}.md"
        new_path = self.done_dir / new_name

        # Update frontmatter with execution results
        with open(file_path, 'r') as f:
            content = f.read()

        updated_content = self._add_execution_result_to_frontmatter(
            content, result, execution_time, status='executed'
        )

        with open(new_path, 'w') as f:
            f.write(updated_content)

        file_path.unlink()
        logger.info(f"Moved to Done: {new_name}")

    def _move_to_failed(self, file_path: Path, result: ExecutionResult, retry_count: int):
        """Move failed action to /Failed/ folder."""
        new_path = self.failed_dir / file_path.name

        # Read current content
        with open(file_path, 'r') as f:
            content = f.read()

        # Update frontmatter
        updated_content = self._add_execution_result_to_frontmatter(
            content, result, 0.0, status='failed', retry_count=retry_count + 1
        )

        with open(new_path, 'w') as f:
            f.write(updated_content)

        file_path.unlink()
        logger.info(f"Moved to Failed: {file_path.name}")

    def _should_retry(self, file_path: Path, retry_count: int) -> bool:
        """Check if enough time has passed for retry."""
        retry_delay = self.retry_backoff * (2 ** retry_count)  # Exponential backoff

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            last_attempt = self._extract_frontmatter_value(content, 'executed_at')
            if not last_attempt:
                return True

            last_time = datetime.fromisoformat(last_attempt.replace('Z', '+00:00'))
            next_retry_time = last_time + timedelta(seconds=retry_delay)

            return datetime.now(last_time.tzinfo) >= next_retry_time
        except:
            return True

    def _get_retry_count(self, file_path: Path) -> int:
        """Get retry count from file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            retry_count_str = self._extract_frontmatter_value(content, 'retry_count')
            return int(retry_count_str) if retry_count_str else 0
        except:
            return 0

    def _extract_frontmatter_value(self, content: str, key: str) -> Optional[str]:
        """Extract value from YAML frontmatter."""
        for line in content.split('\n'):
            if line.startswith(f"{key}:"):
                return line.split(':', 1)[1].strip()
        return None

    def _extract_value(self, content: str, start_marker: str, end_marker: str = '\n', next_line: bool = False) -> Optional[str]:
        """Extract value from markdown."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if start_marker in line:
                if next_line and i + 1 < len(lines):
                    return lines[i + 1].strip()
                else:
                    value = line.split(start_marker, 1)[1] if start_marker in line else ''
                    if end_marker in value:
                        value = value.split(end_marker)[0]
                    return value.strip()
        return None

    def _extract_steps(self, content: str):
        """Extract automation steps from content."""
        steps = []
        in_steps = False
        for line in content.split('\n'):
            if '### Step' in line or '## Browser Automation Steps' in line:
                in_steps = True
            elif in_steps and line.startswith('- '):
                steps.append(line[2:].strip())
        return steps

    def _add_execution_result_to_frontmatter(self, content: str, result: ExecutionResult, execution_time: float, status: str, retry_count: int = 0) -> str:
        """Add execution results to YAML frontmatter."""
        parts = content.split('---')
        if len(parts) < 3:
            return content

        frontmatter = parts[1]
        body = '---'.join(parts[2:])

        # Update frontmatter
        new_frontmatter = frontmatter.rstrip() + f'\nstatus: {status}\nexecuted_at: {result.timestamp}\nexecution_time_seconds: {execution_time:.1f}\nsuccess: {str(result.success).lower()}'

        if result.error:
            new_frontmatter += f'\nerror: {result.error}'
        if result.message_id:
            new_frontmatter += f'\nmessage_id: {result.message_id}'
        if retry_count > 0:
            new_frontmatter += f'\nretry_count: {retry_count}'

        return f"---{new_frontmatter}---{body}"

    def _shutdown(self):
        """Shutdown executor."""
        logger.info("Shutting down MCP Executor")
        self.running = False
        logger.info("MCP Executor stopped")
        sys.exit(0)


def main():
    """Main entry point."""
    Path('logs').mkdir(exist_ok=True)
    executor = MCPExecutor()
    executor.start()


if __name__ == '__main__':
    main()

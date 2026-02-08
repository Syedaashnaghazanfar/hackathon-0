#!/usr/bin/env python3
"""
Bottleneck Detector for CEO Briefing.

Analyzes completed tasks in Done/ folder to detect delays,
calculate severity, and rank bottlenecks for CEO review.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent scripts directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from shared.vault_ops import VaultOps
from shared.error_handler import retry_with_backoff

logger = logging.getLogger(__name__)


class BottleneckDetector:
    """Detect bottlenecks from completed action items."""

    # Severity thresholds
    SEVERITY_NONE = 0
    SEVERITY_LOW = 1      # 1-2 days late
    SEVERITY_MEDIUM = 2   # 3-5 days late
    SEVERITY_HIGH = 3     # 6-10 days late
    SEVERITY_CRITICAL = 4 # 11+ days late

    def __init__(self, vault_path: str):
        """
        Initialize bottleneck detector.

        Args:
            vault_path: Path to Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.vault_ops = VaultOps(vault_path)

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def analyze_completed_tasks(self) -> List[Dict]:
        """
        Analyze all completed tasks in Done/ folder.

        Returns:
            List of completed task dictionaries with:
                - title: Task title
                - completed_date: Actual completion date
                - due_date: Original due date
                - delay_days: Days late (negative if early)
                - category: Task category
                - severity: Bottleneck severity
        """
        done_folder = self.vault_path / 'Done'

        if not done_folder.exists():
            logger.warning("Done/ folder not found, no task completion data")
            return []

        completed_tasks = []

        try:
            for file in done_folder.glob('*.md'):
                task_data = self._parse_done_file(file)
                if task_data:
                    completed_tasks.append(task_data)

            logger.info(f"Analyzed {len(completed_tasks)} completed tasks")
            return completed_tasks
        except Exception as e:
            logger.error(f"Failed to read Done items: {e}")
            return []

    def _parse_done_file(self, file_path: Path) -> Optional[Dict]:
        """
        Parse a completed task file from Done/ folder.

        Args:
            file_path: Path to task markdown file

        Returns:
            Task dictionary or None if parsing fails
        """
        try:
            content, metadata = self.vault_ops.read_markdown(str(file_path))

            # Extract dates from frontmatter or content
            completed_date = metadata.get('completed_date',
                                        metadata.get('date', ''))
            due_date = metadata.get('due_date', '')
            category = metadata.get('category', 'General')
            title = metadata.get('title', file_path.stem)

            # Calculate delay
            delay_days = self.detect_delays(due_date, completed_date)

            # Classify severity
            severity = self.calculate_severity(delay_days)

            return {
                'title': title,
                'completed_date': completed_date,
                'due_date': due_date,
                'delay_days': delay_days,
                'category': category,
                'severity': severity,
                'file_path': str(file_path)
            }
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None

    def detect_delays(self, due_date: str, completed_date: str) -> int:
        """
        Calculate days between due date and completion date.

        Args:
            due_date: Due date string (YYYY-MM-DD format)
            completed_date: Actual completion date string

        Returns:
            Days delay (positive if late, negative if early, 0 if on-time)
        """
        if not due_date or not completed_date:
            return 0

        try:
            due = datetime.strptime(due_date, '%Y-%m-%d')
            completed = datetime.strptime(completed_date, '%Y-%m-%d')

            delay = (completed - due).days
            return delay
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid date format: due={due_date}, completed={completed_date}")
            return 0

    def calculate_severity(self, delay_days: int) -> str:
        """
        Classify bottleneck severity based on delay.

        Args:
            delay_days: Number of days delayed

        Returns:
            Severity level: 'critical', 'high', 'medium', 'low', 'none'
        """
        if delay_days <= 0:
            return 'none'
        elif delay_days <= 2:
            return 'low'
        elif delay_days <= 5:
            return 'medium'
        elif delay_days <= 10:
            return 'high'
        else:
            return 'critical'

    def rank_bottlenecks(self, completed_tasks: List[Dict],
                        top_n: int = 5) -> List[Dict]:
        """
        Rank and return top N bottlenecks by delay.

        Args:
            completed_tasks: List of completed task dictionaries
            top_n: Number of bottlenecks to return (default: 5)

        Returns:
            List of top N bottlenecks, sorted by delay descending
        """
        # Filter only delayed tasks
        bottlenecks = [t for t in completed_tasks if t['delay_days'] > 0]

        # Sort by delay descending (most severe first)
        bottlenecks.sort(key=lambda x: x['delay_days'], reverse=True)

        # Return top N
        return bottlenecks[:top_n]

    def get_bottleneck_summary(self, completed_tasks: List[Dict]) -> Dict:
        """
        Generate bottleneck summary statistics.

        Args:
            completed_tasks: List of completed task dictionaries

        Returns:
            Dictionary with:
                - total_tasks: Total completed tasks
                - bottleneck_count: Number of delayed tasks
                - on_time_count: Number of on-time/early tasks
                - on_time_rate: Percentage on-time
                - severity_breakdown: Count by severity level
                - top_bottlenecks: Top 5 bottlenecks
        """
        total_tasks = len(completed_tasks)
        bottlenecks = [t for t in completed_tasks if t['delay_days'] > 0]
        on_time = [t for t in completed_tasks if t['delay_days'] <= 0]

        bottleneck_count = len(bottlenecks)
        on_time_count = len(on_time)
        on_time_rate = (on_time_count / total_tasks * 100) if total_tasks > 0 else 100.0

        # Severity breakdown
        severity_breakdown = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'none': 0
        }

        for task in completed_tasks:
            severity = task.get('severity', 'none')
            if severity in severity_breakdown:
                severity_breakdown[severity] += 1

        # Top bottlenecks
        top_bottlenecks = self.rank_bottlenecks(completed_tasks, top_n=5)

        return {
            'total_tasks': total_tasks,
            'bottleneck_count': bottleneck_count,
            'on_time_count': on_time_count,
            'on_time_rate': round(on_time_rate, 1),
            'severity_breakdown': severity_breakdown,
            'top_bottlenecks': top_bottlenecks
        }


if __name__ == "__main__":
    # Test bottleneck detector
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "AI_Employee_Vault"

    detector = BottleneckDetector(vault_path)

    # Test analyzing completed tasks
    completed_tasks = detector.analyze_completed_tasks()
    print(f"Analyzed {len(completed_tasks)} completed tasks")

    # Test bottleneck ranking
    top_bottlenecks = detector.rank_bottlenecks(completed_tasks)
    print(f"\nTop {len(top_bottlenecks)} Bottlenecks:")
    for i, bottleneck in enumerate(top_bottlenecks, 1):
        print(f"{i}. {bottleneck['title']} - {bottleneck['delay_days']} days late ({bottleneck['severity']})")

    # Test summary
    summary = detector.get_bottleneck_summary(completed_tasks)
    print(f"\nSummary:")
    print(f"  Total: {summary['total_tasks']}")
    print(f"  On-Time: {summary['on_time_count']} ({summary['on_time_rate']}%)")
    print(f"  Bottlenecks: {summary['bottleneck_count']}")
    print(f"  Severity: {summary['severity_breakdown']}")

"""
Unit tests for bottleneck detector in CEO Briefing.

Tests delay calculation, severity classification, and top 5 sorting
based on task completion delays from Done/ folder action items.
"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))


# Mock bottleneck detector implementation
def calculate_task_delay(
    due_date: str,
    completed_date: str,
    date_format: str = "%Y-%m-%d"
) -> int:
    """
    Calculate days between due date and completion date.

    Args:
        due_date: Due date string
        completed_date: Actual completion date string
        date_format: Date parse format (default: YYYY-MM-DD)

    Returns:
        Days delay (positive if late, negative if early, 0 if on-time)
    """
    try:
        due = datetime.strptime(due_date, date_format)
        completed = datetime.strptime(completed_date, date_format)

        delay = (completed - due).days
        return delay
    except (ValueError, TypeError):
        return 0


def classify_severity(delay_days: int) -> str:
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


def detect_bottlenecks(done_items: list) -> list:
    """
    Detect bottlenecks from completed action items.

    Args:
        done_items: List of dictionaries with:
            - title: Task title
            - due_date: Due date string
            - completed_date: Actual completion date string
            - category: Task category (optional)

    Returns:
        List of bottleneck dictionaries sorted by delay (descending):
            - title: Task title
            - delay_days: Days delayed
            - severity: Severity classification
            - category: Task category
    """
    bottlenecks = []

    for item in done_items:
        due_date = item.get('due_date', '')
        completed_date = item.get('completed_date', '')

        if not due_date or not completed_date:
            continue

        delay = calculate_task_delay(due_date, completed_date)

        if delay > 0:  # Only include delayed tasks
            severity = classify_severity(delay)

            bottleneck = {
                'title': item.get('title', 'Unknown Task'),
                'delay_days': delay,
                'severity': severity,
                'category': item.get('category', 'General')
            }
            bottlenecks.append(bottleneck)

    # Sort by delay (descending - most delayed first)
    bottlenecks.sort(key=lambda x: x['delay_days'], reverse=True)

    return bottlenecks


def get_top_bottlenecks(bottlenecks: list, top_n: int = 5) -> list:
    """
    Get top N bottlenecks by delay.

    Args:
        bottlenecks: List of bottleneck dictionaries (sorted)
        top_n: Number to return (default: 5)

    Returns:
        Top N bottlenecks
    """
    return bottlenecks[:top_n]


class TestBottleneckDetector:
    """Test suite for bottleneck detector."""

    def test_calculate_delay_on_time(self):
        """Test delay calculation when completed on due date."""
        delay = calculate_task_delay(
            due_date="2024-01-15",
            completed_date="2024-01-15"
        )
        assert delay == 0

    def test_calculate_delay_one_day_late(self):
        """Test delay calculation when one day late."""
        delay = calculate_task_delay(
            due_date="2024-01-15",
            completed_date="2024-01-16"
        )
        assert delay == 1

    def test_calculate_delay_one_day_early(self):
        """Test delay calculation when completed one day early."""
        delay = calculate_task_delay(
            due_date="2024-01-15",
            completed_date="2024-01-14"
        )
        assert delay == -1

    def test_calculate_delay_week_late(self):
        """Test delay calculation when one week late."""
        delay = calculate_task_delay(
            due_date="2024-01-15",
            completed_date="2024-01-22"
        )
        assert delay == 7

    def test_calculate_delay_invalid_dates(self):
        """Test delay calculation with invalid dates (returns 0)."""
        delay = calculate_task_delay(
            due_date="invalid-date",
            completed_date="2024-01-16"
        )
        assert delay == 0

    def test_classify_severity_none(self):
        """Test severity classification for on-time or early tasks."""
        assert classify_severity(0) == 'none'
        assert classify_severity(-1) == 'none'
        assert classify_severity(-10) == 'none'

    def test_classify_severity_low(self):
        """Test severity classification for 1-2 day delays."""
        assert classify_severity(1) == 'low'
        assert classify_severity(2) == 'low'

    def test_classify_severity_medium(self):
        """Test severity classification for 3-5 day delays."""
        assert classify_severity(3) == 'medium'
        assert classify_severity(4) == 'medium'
        assert classify_severity(5) == 'medium'

    def test_classify_severity_high(self):
        """Test severity classification for 6-10 day delays."""
        assert classify_severity(6) == 'high'
        assert classify_severity(8) == 'high'
        assert classify_severity(10) == 'high'

    def test_classify_severity_critical(self):
        """Test severity classification for 11+ day delays."""
        assert classify_severity(11) == 'critical'
        assert classify_severity(15) == 'critical'
        assert classify_severity(30) == 'critical'

    def test_detect_bottlenecks_empty_list(self):
        """Test bottleneck detection with empty done items list."""
        bottlenecks = detect_bottlenecks([])
        assert len(bottlenecks) == 0

    def test_detect_bottlenecks_all_on_time(self):
        """Test bottleneck detection when all tasks on time."""
        items = [
            {
                'title': 'Task A',
                'due_date': '2024-01-15',
                'completed_date': '2024-01-15',
                'category': 'Development'
            },
            {
                'title': 'Task B',
                'due_date': '2024-01-16',
                'completed_date': '2024-01-14',  # Early
                'category': 'Design'
            }
        ]
        bottlenecks = detect_bottlenecks(items)
        assert len(bottlenecks) == 0

    def test_detect_bottlenecks_mixed_delays(self):
        """Test bottleneck detection with mixed on-time and delayed tasks."""
        items = [
            {
                'title': 'Task On Time',
                'due_date': '2024-01-15',
                'completed_date': '2024-01-15',
                'category': 'Development'
            },
            {
                'title': 'Task Late 3 Days',
                'due_date': '2024-01-15',
                'completed_date': '2024-01-18',
                'category': 'Design'
            },
            {
                'title': 'Task Late 7 Days',
                'due_date': '2024-01-10',
                'completed_date': '2024-01-17',
                'category': 'Marketing'
            },
            {
                'title': 'Task Early',
                'due_date': '2024-01-20',
                'completed_date': '2024-01-18',
                'category': 'Sales'
            }
        ]
        bottlenecks = detect_bottlenecks(items)

        # Only delayed tasks included
        assert len(bottlenecks) == 2

        # Sorted by delay descending
        assert bottlenecks[0]['title'] == 'Task Late 7 Days'
        assert bottlenecks[0]['delay_days'] == 7
        assert bottlenecks[0]['severity'] == 'high'

        assert bottlenecks[1]['title'] == 'Task Late 3 Days'
        assert bottlenecks[1]['delay_days'] == 3
        assert bottlenecks[1]['severity'] == 'medium'

    def test_detect_bottlenecks_missing_dates(self):
        """Test bottleneck detection with missing date fields."""
        items = [
            {
                'title': 'Task No Dates',
                'category': 'Development'
            },
            {
                'title': 'Task Only Due Date',
                'due_date': '2024-01-15',
                'category': 'Design'
            },
            {
                'title': 'Task Only Completed Date',
                'completed_date': '2024-01-18',
                'category': 'Marketing'
            }
        ]
        bottlenecks = detect_bottlenecks(items)

        # Items without both dates skipped
        assert len(bottlenecks) == 0

    def test_detect_bottlenecks_sorting(self):
        """Test that bottlenecks are sorted by delay (most severe first)."""
        items = [
            {'title': 'Task 1 Day', 'due_date': '2024-01-15', 'completed_date': '2024-01-16'},
            {'title': 'Task 15 Days', 'due_date': '2024-01-01', 'completed_date': '2024-01-16'},
            {'title': 'Task 5 Days', 'due_date': '2024-01-10', 'completed_date': '2024-01-15'},
            {'title': 'Task 8 Days', 'due_date': '2024-01-08', 'completed_date': '2024-01-16'},
            {'title': 'Task 3 Days', 'due_date': '2024-01-12', 'completed_date': '2024-01-15'},
        ]
        bottlenecks = detect_bottlenecks(items)

        delays = [b['delay_days'] for b in bottlenecks]
        assert delays == [15, 8, 5, 3, 1]

    def test_get_top_bottlenecks_less_than_n(self):
        """Test getting top N when fewer than N bottlenecks exist."""
        bottlenecks = [
            {'title': 'Task A', 'delay_days': 5, 'severity': 'medium', 'category': 'Dev'},
            {'title': 'Task B', 'delay_days': 3, 'severity': 'medium', 'category': 'Design'},
        ]
        top = get_top_bottlenecks(bottlenecks, top_n=5)

        assert len(top) == 2  # Returns all available
        assert top[0]['title'] == 'Task A'
        assert top[1]['title'] == 'Task B'

    def test_get_top_bottlenecks_exactly_n(self):
        """Test getting top N when exactly N bottlenecks exist."""
        bottlenecks = [
            {'title': f'Task {i}', 'delay_days': 10 - i, 'severity': 'high', 'category': 'Dev'}
            for i in range(1, 6)
        ]
        top = get_top_bottlenecks(bottlenecks, top_n=5)

        assert len(top) == 5
        assert top[0]['delay_days'] == 9  # Highest delay

    def test_get_top_bottlenecks_more_than_n(self):
        """Test getting top N when more than N bottlenecks exist."""
        bottlenecks = [
            {'title': f'Task {i}', 'delay_days': 20 - i, 'severity': 'critical', 'category': 'Dev'}
            for i in range(1, 11)
        ]
        top = get_top_bottlenecks(bottlenecks, top_n=5)

        assert len(top) == 5  # Only top 5
        assert top[0]['delay_days'] == 19  # Highest delay
        assert top[4]['delay_days'] == 15  # 5th highest

    def test_bottleneck_count_for_health_score(self):
        """Test integration with health score formula (bottleneck penalty)."""
        items = [
            {'title': 'Task 1 Day', 'due_date': '2024-01-15', 'completed_date': '2024-01-16'},
            {'title': 'Task 3 Days', 'due_date': '2024-01-12', 'completed_date': '2024-01-15'},
            {'title': 'Task 7 Days', 'due_date': '2024-01-08', 'completed_date': '2024-01-15'},
        ]
        bottlenecks = detect_bottlenecks(items)

        # 3 bottlenecks = -30 point penalty
        bottleneck_count = len(bottlenecks)
        assert bottleneck_count == 3

        # With 80% revenue, 90% on-time, 3 bottlenecks
        # health_score = (80 * 0.5 + 90 * 0.5) - 30 = 85 - 30 = 55
        from test_health_score import calculate_health_score
        health_score = calculate_health_score(80.0, 90.0, bottleneck_count)
        assert health_score == 55

    def test_bottleneck_severity_distribution(self):
        """Test severity distribution across many bottlenecks."""
        items = [
            {'title': f'Task {d} Days', 'due_date': '2024-01-01', 'completed_date': f'2024-01-{1+d}'}
            for d in [1, 2, 3, 5, 7, 10, 12, 15]
        ]
        bottlenecks = detect_bottlenecks(items)

        severities = [b['severity'] for b in bottlenecks]

        assert severities.count('low') == 2      # 1, 2 days
        assert severities.count('medium') == 2   # 3, 5 days
        assert severities.count('high') == 2     # 7, 10 days
        assert severities.count('critical') == 2 # 12, 15 days


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

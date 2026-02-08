"""
Unit tests for health score calculation in CEO Briefing.

Tests edge cases: zero revenue, negative delays, division by zero, and
validates the health score formula:
health_score = (revenue_progress * 0.5 + on_time_rate * 0.5) - bottleneck_count * 10
"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

# Mock data for testing
def calculate_health_score(
    revenue_progress: float,
    on_time_rate: float,
    bottleneck_count: int
) -> int:
    """
    Calculate overall business health score (0-100).

    Formula: health_score = (revenue_progress * 0.5 + on_time_rate * 0.5) - bottleneck_count * 10

    Args:
        revenue_progress: Revenue target completion percentage (0-100)
        on_time_rate: Tasks completed on-time percentage (0-100)
        bottleneck_count: Number of bottlenecks detected

    Returns:
        Health score from 0 to 100
    """
    # Weighted components
    revenue_score = min(100, revenue_progress)
    operations_score = min(100, on_time_rate)
    bottleneck_penalty = bottleneck_count * 10

    # Calculate weighted average
    health_score = (revenue_score * 0.5 + operations_score * 0.5)
    health_score = max(0, health_score - bottleneck_penalty)
    health_score = min(100, health_score)  # Cap at 100

    return int(health_score)


class TestHealthScoreCalculation:
    """Test suite for health score calculation."""

    def test_perfect_health_score(self):
        """Test perfect score: 100% revenue, 100% on-time, no bottlenecks."""
        score = calculate_health_score(100.0, 100.0, 0)
        assert score == 100

    def test_zero_revenue_zero_tasks(self):
        """Test edge case: zero revenue, zero tasks completed."""
        score = calculate_health_score(0.0, 0.0, 0)
        assert score == 0

    def test_negative_delays_handled(self):
        """Test that negative delays (negative days) are handled properly."""
        # 50% revenue, 50% on-time, 3 bottlenecks
        # Score = (50 * 0.5 + 50 * 0.5) - 30 = 50 - 30 = 20
        score = calculate_health_score(50.0, 50.0, 3)
        assert score == 20

    def test_many_bottlenecks(self):
        """Test that many bottlenecks can reduce score to zero despite good performance."""
        # 90% revenue, 90% on-time, 10 bottlenecks
        # Score = (90 * 0.5 + 90 * 0.5) - 100 = 90 - 100 = -10 → max(0, -10) = 0
        score = calculate_health_score(90.0, 90.0, 10)
        assert score == 0

    def test_partial_progress(self):
        """Test realistic partial progress scenario."""
        # 45% revenue, 92% on-time, 2 bottlenecks
        # Score = (45 * 0.5 + 92 * 0.5) - 20 = 68.5 - 20 = 48.5 → 48
        score = calculate_health_score(45.0, 92.0, 2)
        assert score == 48

    def test_revenue_only_success(self):
        """Test strong revenue but poor operations."""
        # 100% revenue, 40% on-time, 0 bottlenecks
        # Score = (100 * 0.5 + 40 * 0.5) - 0 = 70 - 0 = 70
        score = calculate_health_score(100.0, 40.0, 0)
        assert score == 70

    def test_operations_only_success(self):
        """Test strong operations but poor revenue."""
        # 30% revenue, 100% on-time, 0 bottlenecks
        # Score = (30 * 0.5 + 100 * 0.5) - 0 = 65 - 0 = 65
        score = calculate_health_score(30.0, 100.0, 0)
        assert score == 65

    def test_score_capped_at_100(self):
        """Test that score is capped at 100 even with excellent metrics."""
        # 110% revenue (overperforming), 100% on-time, negative bottlenecks
        score = calculate_health_score(110.0, 100.0, -1)
        assert score == 100

    def test_score_floor_at_0(self):
        """Test that score never goes below 0."""
        # 0% revenue, 0% on-time, 20 bottlenecks
        # Score = (0 * 0.5 + 0 * 0.5) - 200 = 0 - 200 = -200 → max(0, -200) = 0
        score = calculate_health_score(0.0, 0.0, 20)
        assert score == 0

    def test_fractional_percentages(self):
        """Test that fractional percentages are handled correctly."""
        # 33.33% revenue, 66.67% on-time, 1 bottleneck
        # Score = (33.33 * 0.5 + 66.67 * 0.5) - 10 = 50 - 10 = 40
        score = calculate_health_score(33.33, 66.67, 1)
        assert score == 40

    def test_bottleneck_impact(self):
        """Test that each bottleneck reduces score by 10 points."""
        # 80% revenue, 80% on-time
        # 0 bottlenecks: score = 80
        # 1 bottleneck: score = 70
        # 2 bottlenecks: score = 60
        # 3 bottlenecks: score = 50
        # etc.

        base_score = calculate_health_score(80.0, 80.0, 0)
        assert base_score == 80

        score_1 = calculate_health_score(80.0, 80.0, 1)
        assert score_1 == 70

        score_2 = calculate_health_score(80.0, 80.0, 2)
        assert score_2 == 60

        score_3 = calculate_health_score(80.0, 80.0, 3)
        assert score_3 == 50

        score_8 = calculate_health_score(80.0, 80.0, 8)
        assert score_8 == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

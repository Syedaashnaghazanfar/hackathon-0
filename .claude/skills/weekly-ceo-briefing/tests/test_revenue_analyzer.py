"""
Unit tests for revenue analyzer in CEO Briefing.

Tests markdown table parsing, amount extraction, and revenue progress
calculation from Accounting/Current_Month.md files.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))


# Mock revenue analyzer implementation
def parse_revenue_from_markdown(content: str) -> dict:
    """
    Parse revenue data from Accounting/Current_Month.md markdown content.

    Expected format:
    | Invoice | Amount | Date | Status |
    |---------|--------|------|--------|
    | INV-001 | 5000.00 | 2024-01-15 | Paid |

    Args:
        content: Markdown file content

    Returns:
        Dictionary with:
            - paid_invoices: list of paid invoice amounts
            - pending_invoices: list of pending invoice amounts
            - total_paid: sum of paid invoices
            - total_pending: sum of pending invoices
            - currency: extracted currency symbol (default 'USD')
    """
    lines = content.strip().split('\n')

    # Find table start
    table_start = -1
    for i, line in enumerate(lines):
        if '| Invoice |' in line or '|invoice|' in line.lower():
            table_start = i
            break

    if table_start == -1:
        return {
            'paid_invoices': [],
            'pending_invoices': [],
            'total_paid': 0.0,
            'total_pending': 0.0,
            'currency': 'USD'
        }

    # Skip header and separator
    data_lines = []
    for line in lines[table_start + 2:]:
        if '|' in line and line.strip():
            data_lines.append(line)

    paid_invoices = []
    pending_invoices = []
    currency = 'USD'

    for line in data_lines:
        parts = [p.strip() for p in line.split('|')]
        # Filter out empty strings
        parts = [p for p in parts if p]

        if len(parts) >= 4:
            # Format: Invoice | Amount | Date | Status
            invoice_id = parts[0]
            amount_str = parts[1]
            date_str = parts[2] if len(parts) > 2 else ''
            status = parts[3] if len(parts) > 3 else ''

            # Extract currency symbol from amount (only first currency detected)
            if currency == 'USD':  # Only set if still default
                if '€' in amount_str:
                    currency = 'EUR'
                elif '£' in amount_str:
                    currency = 'GBP'
                elif '$' in amount_str:
                    currency = 'USD'

            # Clean amount string (remove currency symbols, commas)
            amount_clean = amount_str.replace('€', '').replace('£', '').replace('$', '')
            amount_clean = amount_clean.replace(',', '').strip()

            try:
                amount = float(amount_clean)

                if status.lower() in ['paid', 'cleared', 'complete']:
                    paid_invoices.append(amount)
                elif status.lower() in ['pending', 'outstanding', 'sent', 'draft']:
                    pending_invoices.append(amount)
            except ValueError:
                continue

    return {
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'total_paid': sum(paid_invoices),
        'total_pending': sum(pending_invoices),
        'currency': currency
    }


def calculate_revenue_progress(
    total_paid: float,
    monthly_target: float
) -> float:
    """
    Calculate revenue progress percentage.

    Args:
        total_paid: Total revenue collected this month
        monthly_target: Monthly revenue target from Business_Goals.md

    Returns:
        Progress percentage (0-100+)
    """
    if monthly_target <= 0:
        return 0.0

    progress = (total_paid / monthly_target) * 100.0
    return round(progress, 2)


class TestRevenueAnalyzer:
    """Test suite for revenue analyzer."""

    def test_parse_standard_table(self):
        """Test parsing standard invoice table with mixed statuses."""
        content = """
# Accounting January 2024

| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $5,000.00 | 2024-01-15 | Paid |
| INV-002 | $3,250.50 | 2024-01-20 | Pending |
| INV-003 | $7,500.00 | 2024-01-25 | Paid |
| INV-004 | $1,200.00 | 2024-01-28 | Outstanding |
"""
        result = parse_revenue_from_markdown(content)

        assert result['total_paid'] == 12500.00  # 5000 + 7500
        assert result['total_pending'] == 4450.50  # 3250.50 + 1200
        assert len(result['paid_invoices']) == 2
        assert len(result['pending_invoices']) == 2
        assert result['currency'] == 'USD'

    def test_parse_empty_file(self):
        """Test parsing file with no table."""
        content = """
# Accounting January 2024

No invoices yet.
"""
        result = parse_revenue_from_markdown(content)

        assert result['total_paid'] == 0.0
        assert result['total_pending'] == 0.0
        assert len(result['paid_invoices']) == 0
        assert len(result['pending_invoices']) == 0

    def test_parse_different_currency_symbols(self):
        """Test parsing different currency symbols."""
        content = """
# Accounting January 2024

| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | €5,000.00 | 2024-01-15 | Paid |
| INV-002 | £3,250.50 | 2024-01-20 | Paid |
"""
        result = parse_revenue_from_markdown(content)

        # Detects first currency found
        assert result['currency'] == 'EUR'
        assert result['total_paid'] == 8250.50

    def test_parse_mixed_case_status(self):
        """Test parsing with different status capitalizations."""
        content = """
| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $1,000.00 | 2024-01-15 | paid |
| INV-002 | $2,000.00 | 2024-01-20 | PAID |
| INV-003 | $3,000.00 | 2024-01-25 | Paid |
| INV-004 | $1,500.00 | 2024-01-28 | PENDING |
| INV-005 | $2,500.00 | 2024-01-30 | outstanding |
"""
        result = parse_revenue_from_markdown(content)

        # All variants of "paid" recognized
        assert result['total_paid'] == 6000.00
        # All variants of "pending" recognized
        assert result['total_pending'] == 4000.00

    def test_parse_alternative_status_values(self):
        """Test parsing with alternative status values."""
        content = """
| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $1,000.00 | 2024-01-15 | Cleared |
| INV-002 | $2,000.00 | 2024-01-20 | Complete |
| INV-003 | $1,500.00 | 2024-01-25 | Sent |
| INV-004 | $2,500.00 | 2024-01-30 | Draft |
"""
        result = parse_revenue_from_markdown(content)

        # Cleared and Complete treated as paid
        assert result['total_paid'] == 3000.00
        # Sent and Draft treated as pending
        assert result['total_pending'] == 4000.00

    def test_parse_malformed_amounts(self):
        """Test handling of malformed amount strings."""
        content = """
| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $1,000.00 | 2024-01-15 | Paid |
| INV-002 | invalid | 2024-01-20 | Paid |
| INV-003 | $2,500.50 | 2024-01-25 | Pending |
"""
        result = parse_revenue_from_markdown(content)

        # Invalid amounts skipped
        assert result['total_paid'] == 1000.00
        assert result['total_pending'] == 2500.50
        assert len(result['paid_invoices']) == 1

    def test_calculate_progress_on_target(self):
        """Test progress calculation when exactly on target."""
        progress = calculate_revenue_progress(
            total_paid=10000.0,
            monthly_target=10000.0
        )
        assert progress == 100.0

    def test_calculate_progress_half_target(self):
        """Test progress calculation at 50% of target."""
        progress = calculate_revenue_progress(
            total_paid=5000.0,
            monthly_target=10000.0
        )
        assert progress == 50.0

    def test_calculate_progress_exceeds_target(self):
        """Test progress calculation when exceeding target."""
        progress = calculate_revenue_progress(
            total_paid=12500.0,
            monthly_target=10000.0
        )
        assert progress == 125.0

    def test_calculate_progress_zero_target(self):
        """Test progress calculation with zero target (avoid division by zero)."""
        progress = calculate_revenue_progress(
            total_paid=5000.0,
            monthly_target=0.0
        )
        assert progress == 0.0

    def test_calculate_progress_negative_target(self):
        """Test progress calculation with negative target (treated as zero)."""
        progress = calculate_revenue_progress(
            total_paid=5000.0,
            monthly_target=-1000.0
        )
        assert progress == 0.0

    def test_revenue_progress_rounding(self):
        """Test that revenue progress is rounded to 2 decimal places."""
        progress = calculate_revenue_progress(
            total_paid=3333.33,
            monthly_target=10000.0
        )
        assert progress == 33.33

    def test_integration_revenue_to_health_score(self):
        """Test integration with health score formula."""
        # Parse revenue data
        content = """
| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $4,500.00 | 2024-01-15 | Paid |
| INV-002 | $2,250.00 | 2024-01-20 | Paid |
"""
        revenue_data = parse_revenue_from_markdown(content)

        # Calculate progress
        progress = calculate_revenue_progress(
            total_paid=revenue_data['total_paid'],
            monthly_target=10000.0
        )

        # Should be 67.5% revenue progress
        assert progress == 67.5

        # If on-time rate is 92% and 2 bottlenecks
        # health_score = (67.5 * 0.5 + 92 * 0.5) - 20 = 79.75 - 20 = 59.75 → 59
        from test_health_score import calculate_health_score
        health_score = calculate_health_score(progress, 92.0, 2)
        assert health_score == 59


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

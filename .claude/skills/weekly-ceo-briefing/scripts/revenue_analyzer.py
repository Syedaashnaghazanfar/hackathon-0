#!/usr/bin/env python3
"""
Revenue Analyzer for CEO Briefing.

Analyzes revenue data from Accounting/Current_Month.md, calculates
month-to-date progress against targets, and extracts transaction details.
"""

import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent scripts directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from shared.vault_ops import VaultOps
from shared.error_handler import retry_with_backoff
from shared.frontmatter_validator import VaultMetadata

logger = logging.getLogger(__name__)


class RevenueAnalyzer:
    """Analyze revenue data from Obsidian vault."""

    def __init__(self, vault_path: str):
        """
        Initialize revenue analyzer.

        Args:
            vault_path: Path to Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.vault_ops = VaultOps(vault_path)

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def load_business_goals(self) -> Dict:
        """
        Load business goals from Business_Goals.md.

        Returns:
            Dictionary with:
                - monthly_revenue_target: Float target
                - weekly_task_target: Integer target
                - active_projects: List of project names
                - audit_rules: Dict of audit configuration
        """
        goals_file = self.vault_path / 'Business_Goals.md'

        if not goals_file.exists():
            logger.warning("Business_Goals.md not found, using default targets")
            return {
                'monthly_revenue_target': 10000.0,
                'weekly_task_target': 20,
                'active_projects': [],
                'audit_rules': {}
            }

        try:
            content, metadata = self.vault_ops.read_markdown(str(goals_file))

            # Extract targets from frontmatter or content
            monthly_target = metadata.get('monthly_revenue_target',
                                        metadata.get('revenue_target', 10000.0))

            # Handle currency symbols in target
            if isinstance(monthly_target, str):
                # Remove $, €, £, commas
                monthly_target = monthly_target.replace('$', '').replace('€', '').replace('£', '')
                monthly_target = monthly_target.replace(',', '').strip()
                monthly_target = float(monthly_target)

            return {
                'monthly_revenue_target': float(monthly_target),
                'weekly_task_target': metadata.get('weekly_task_target', 20),
                'active_projects': metadata.get('active_projects', []),
                'audit_rules': metadata.get('audit_rules', {})
            }
        except Exception as e:
            logger.error(f"Failed to parse Business_Goals.md: {e}")
            return {
                'monthly_revenue_target': 10000.0,
                'weekly_task_target': 20,
                'active_projects': [],
                'audit_rules': {}
            }

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def analyze_revenue(self) -> Dict:
        """
        Analyze revenue from Accounting/Current_Month.md.

        Returns:
            Dictionary with:
                - total_paid: Total paid invoices
                - total_pending: Total pending invoices
                - invoices_paid: Count of paid invoices
                - invoices_pending: Count of pending invoices
                - transactions: List of transaction details
                - currency: Detected currency (USD, EUR, GBP)
                - mtd_progress: Month-to-date progress percentage
        """
        accounting_file = self.vault_path / 'Accounting' / 'Current_Month.md'

        if not accounting_file.exists():
            logger.warning("Accounting/Current_Month.md not found, using zero revenue")
            return {
                'total_paid': 0.0,
                'total_pending': 0.0,
                'invoices_paid': 0,
                'invoices_pending': 0,
                'transactions': [],
                'currency': 'USD',
                'mtd_progress': 0.0
            }

        try:
            content, metadata = self.vault_ops.read_markdown(str(accounting_file))
            transactions = self._extract_transactions(content)

            total_paid = sum(t['amount'] for t in transactions if t['status'] == 'paid')
            total_pending = sum(t['amount'] for t in transactions if t['status'] == 'pending')
            invoices_paid = len([t for t in transactions if t['status'] == 'paid'])
            invoices_pending = len([t for t in transactions if t['status'] == 'pending'])

            # Detect currency from first transaction
            currency = transactions[0]['currency'] if transactions else 'USD'

            result = {
                'total_paid': total_paid,
                'total_pending': total_pending,
                'invoices_paid': invoices_paid,
                'invoices_pending': invoices_pending,
                'transactions': transactions,
                'currency': currency,
                'mtd_progress': 0.0  # Will be calculated with target
            }

            return result
        except Exception as e:
            logger.error(f"Failed to parse Accounting data: {e}")
            return {
                'total_paid': 0.0,
                'total_pending': 0.0,
                'invoices_paid': 0,
                'invoices_pending': 0,
                'transactions': [],
                'currency': 'USD',
                'mtd_progress': 0.0
            }

    def _extract_transactions(self, content: str) -> List[Dict]:
        """
        Extract transaction details from markdown table.

        Expected format:
        | Invoice | Amount | Date | Status |
        |---------|--------|------|--------|
        | INV-001 | $5,000.00 | 2024-01-15 | Paid |

        Args:
            content: Markdown file content

        Returns:
            List of transaction dictionaries
        """
        lines = content.strip().split('\n')
        transactions = []

        # Find table start
        table_start = -1
        for i, line in enumerate(lines):
            if '| Invoice |' in line or '|invoice|' in line.lower():
                table_start = i
                break

        if table_start == -1:
            return transactions

        # Skip header and separator
        for line in lines[table_start + 2:]:
            if '|' in line and line.strip():
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]  # Remove empty strings

                if len(parts) >= 4:
                    invoice_id = parts[0]
                    amount_str = parts[1]
                    date_str = parts[2]
                    status = parts[3]

                    # Detect currency
                    currency = 'USD'
                    if '€' in amount_str:
                        currency = 'EUR'
                    elif '£' in amount_str:
                        currency = 'GBP'

                    # Clean amount string
                    amount_clean = amount_str.replace('€', '').replace('£', '').replace('$', '')
                    amount_clean = amount_clean.replace(',', '').strip()

                    try:
                        amount = float(amount_clean)

                        # Normalize status
                        status_lower = status.lower()
                        if status_lower in ['paid', 'cleared', 'complete']:
                            normalized_status = 'paid'
                        elif status_lower in ['pending', 'outstanding', 'sent', 'draft']:
                            normalized_status = 'pending'
                        else:
                            normalized_status = status_lower

                        transactions.append({
                            'invoice_id': invoice_id,
                            'amount': amount,
                            'date': date_str,
                            'status': normalized_status,
                            'currency': currency
                        })
                    except ValueError:
                        logger.warning(f"Could not parse amount: {amount_str}")
                        continue

        return transactions

    def calculate_mtd(self, revenue_data: Dict, monthly_target: float) -> float:
        """
        Calculate month-to-date revenue progress percentage.

        Args:
            revenue_data: Revenue analysis result
            monthly_target: Monthly revenue target from business goals

        Returns:
            Progress percentage (0-100+)
        """
        if monthly_target <= 0:
            return 0.0

        total_paid = revenue_data.get('total_paid', 0.0)
        progress = (total_paid / monthly_target) * 100.0

        return round(progress, 2)


if __name__ == "__main__":
    # Test revenue analyzer
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "AI_Employee_Vault"

    analyzer = RevenueAnalyzer(vault_path)

    # Test loading business goals
    goals = analyzer.load_business_goals()
    print(f"Business Goals: {goals}")

    # Test analyzing revenue
    revenue = analyzer.analyze_revenue()
    print(f"Revenue Analysis: {revenue}")

    # Test MTD calculation
    if revenue['transactions']:
        mtd = analyzer.calculate_mtd(revenue, goals['monthly_revenue_target'])
        print(f"MTD Progress: {mtd}%")

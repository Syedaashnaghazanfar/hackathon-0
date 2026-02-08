#!/usr/bin/env python3
"""
Cost Optimizer for CEO Briefing.

Analyzes subscriptions, detects unused tools, calculates potential savings,
and flags cost increases for financial optimization opportunities.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import re

# Add parent scripts directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from shared.vault_ops import VaultOps
from shared.error_handler import retry_with_backoff

logger = logging.getLogger(__name__)


class CostOptimizer:
    """Analyze and optimize business costs."""

    def __init__(self, vault_path: str):
        """
        Initialize cost optimizer.

        Args:
            vault_path: Path to Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.vault_ops = VaultOps(vault_path)

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def analyze_subscriptions(self) -> List[Dict]:
        """
        Analyze subscription expenses from Accounting/Subscriptions.md.

        Returns:
            List of subscription dictionaries with:
                - name: Subscription/service name
                - cost: Monthly cost
                - category: Software, infrastructure, etc.
                - billing_date: Day of month billed
                - status: active, cancelled, trial
        """
        subscriptions_file = self.vault_path / 'Accounting' / 'Subscriptions.md'

        if not subscriptions_file.exists():
            logger.info("Accounting/Subscriptions.md not found, no subscription data")
            return []

        try:
            content, metadata = self.vault_ops.read_markdown(str(subscriptions_file))
            subscriptions = self._parse_subscription_table(content)

            logger.info(f"Analyzed {len(subscriptions)} subscriptions")
            return subscriptions
        except Exception as e:
            logger.error(f"Failed to parse Subscriptions data: {e}")
            return []

    def _parse_subscription_table(self, content: str) -> List[Dict]:
        """
        Parse subscription table from markdown content.

        Expected format:
        | Service | Cost | Category | Billing Date | Status |
        |---------|------|----------|--------------|--------|
        | GitHub | $10/mo | Software | 15 | active |

        Args:
            content: Markdown file content

        Returns:
            List of subscription dictionaries
        """
        lines = content.strip().split('\n')
        subscriptions = []

        # Find table start
        table_start = -1
        for i, line in enumerate(lines):
            if '| Service |' in line or '|service|' in line.lower():
                table_start = i
                break

        if table_start == -1:
            return subscriptions

        # Skip header and separator
        for line in lines[table_start + 2:]:
            if '|' in line and line.strip():
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]

                if len(parts) >= 5:
                    name = parts[0]
                    cost_str = parts[1]
                    category = parts[2]
                    billing_date = parts[3]
                    status = parts[4]

                    # Parse cost (remove $, /mo, convert to float)
                    cost_clean = cost_str.replace('$', '').replace('/mo', '').replace(',', '').strip()
                    try:
                        cost = float(cost_clean)
                    except ValueError:
                        cost = 0.0

                    subscriptions.append({
                        'name': name,
                        'cost': cost,
                        'category': category,
                        'billing_date': billing_date,
                        'status': status.lower()
                    })

        return subscriptions

    def detect_unused_tools(self, subscriptions: List[Dict],
                           days_threshold: int = 90) -> List[Dict]:
        """
        Detect potentially unused tools based on last usage.

        Args:
            subscriptions: List of subscription dictionaries
            days_threshold: Days without use to flag as unused (default: 90)

        Returns:
            List of unused tool recommendations with:
                - name: Tool name
                - cost: Monthly cost
                - last_used: Last usage date (if available)
                - potential_savings: Annual savings if cancelled
        """
        unused_tools = []

        # For now, this is a placeholder that checks for cancelled trials
        # In production, would integrate with usage analytics APIs
        for sub in subscriptions:
            if sub['status'] in ['trial', 'inactive']:
                annual_cost = sub['cost'] * 12
                unused_tools.append({
                    'name': sub['name'],
                    'cost': sub['cost'],
                    'last_used': None,
                    'potential_savings': annual_cost,
                    'reason': f"Status is {sub['status']}, consider cancelling"
                })

        logger.info(f"Detected {len(unused_tools)} potentially unused tools")
        return unused_tools

    def calculate_savings(self, unused_tools: List[Dict]) -> Dict:
        """
        Calculate total potential savings from optimizations.

        Args:
            unused_tools: List of unused tool recommendations

        Returns:
            Dictionary with:
                - monthly_savings: Total monthly savings
                - annual_savings: Total annual savings
                - recommendations: List of tools to cancel/downgrade
        """
        monthly_savings = sum(tool['potential_savings'] / 12 for tool in unused_tools)
        annual_savings = sum(tool['potential_savings'] for tool in unused_tools)

        return {
            'monthly_savings': round(monthly_savings, 2),
            'annual_savings': round(annual_savings, 2),
            'recommendations': unused_tools
        }

    def flag_cost_increases(self, current_month_expenses: List[Dict],
                           previous_month_expenses: List[Dict],
                           threshold: float = 0.15) -> List[Dict]:
        """
        Flag significant cost increases compared to previous month.

        Args:
            current_month_expenses: Current month expense list
            previous_month_expenses: Previous month expense list
            threshold: Percentage increase threshold (default: 15%)

        Returns:
            List of cost increase alerts with:
                - category: Expense category
                - previous_cost: Previous month cost
                - current_cost: Current month cost
                - increase_percent: Percentage increase
                - increase_amount: Dollar amount increase
        """
        alerts = []

        # Build expense map by category
        previous_map = {exp['category']: exp['amount'] for exp in previous_month_expenses}
        current_map = {exp['category']: exp['amount'] for exp in current_month_expenses}

        # Compare categories
        all_categories = set(previous_map.keys()) | set(current_map.keys())

        for category in all_categories:
            previous_cost = previous_map.get(category, 0)
            current_cost = current_map.get(category, 0)

            if previous_cost > 0:  # Only compare if previous data exists
                increase_percent = ((current_cost - previous_cost) / previous_cost) * 100

                if increase_percent > (threshold * 100):
                    alerts.append({
                        'category': category,
                        'previous_cost': previous_cost,
                        'current_cost': current_cost,
                        'increase_percent': round(increase_percent, 1),
                        'increase_amount': round(current_cost - previous_cost, 2)
                    })

        logger.info(f"Flagged {len(alerts)} cost increases above {threshold*100}% threshold")
        return alerts

    def generate_optimization_report(self) -> Dict:
        """
        Generate comprehensive cost optimization report.

        Returns:
            Dictionary with:
                - subscriptions: Active subscriptions list
                - unused_tools: Tools to consider cancelling
                - savings_summary: Total potential savings
                - cost_increases: Significant cost increases
                - recommendations: Actionable recommendations
        """
        # Analyze subscriptions
        subscriptions = self.analyze_subscriptions()

        # Detect unused tools
        unused_tools = self.detect_unused_tools(subscriptions)

        # Calculate savings
        savings_summary = self.calculate_savings(unused_tools)

        # For cost increases, need expense data (placeholder)
        cost_increases = []  # Would require monthly expense comparison

        # Generate recommendations
        recommendations = []

        if unused_tools:
            recommendations.append({
                'priority': 'high',
                'action': 'cancel_unused_tools',
                'description': f"Cancel {len(unused_tools)} unused subscriptions",
                'potential_savings': savings_summary['annual_savings']
            })

        return {
            'subscriptions': subscriptions,
            'unused_tools': unused_tools,
            'savings_summary': savings_summary,
            'cost_increases': cost_increases,
            'recommendations': recommendations
        }


if __name__ == "__main__":
    # Test cost optimizer
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "AI_Employee_Vault"

    optimizer = CostOptimizer(vault_path)

    # Test subscription analysis
    subscriptions = optimizer.analyze_subscriptions()
    print(f"Subscriptions: {len(subscriptions)}")

    # Test unused tool detection
    unused_tools = optimizer.detect_unused_tools(subscriptions)
    print(f"Unused tools: {len(unused_tools)}")

    # Test savings calculation
    if unused_tools:
        savings = optimizer.calculate_savings(unused_tools)
        print(f"Potential monthly savings: ${savings['monthly_savings']}")
        print(f"Potential annual savings: ${savings['annual_savings']}")

    # Test optimization report
    report = optimizer.generate_optimization_report()
    print(f"\nOptimization Report:")
    print(f"  Active subscriptions: {len(report['subscriptions'])}")
    print(f"  Recommendations: {len(report['recommendations'])}")

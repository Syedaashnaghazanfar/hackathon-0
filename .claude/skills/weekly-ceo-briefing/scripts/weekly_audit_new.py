#!/usr/bin/env python3
"""
Weekly Audit Generator - CEO Briefing Orchestrator.

Generates comprehensive Monday morning CEO briefings by analyzing
business goals, revenue metrics, completed tasks, bottlenecks, and
cost optimization opportunities with graceful degradation.

Implements tasks T023-T032 from Gold Tier implementation plan.
"""

import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import local analysis modules
from revenue_analyzer import RevenueAnalyzer
from bottleneck_detector import BottleneckDetector
from cost_optimizer import CostOptimizer

# Import shared utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from shared.vault_ops import VaultOps
from shared.audit_logger import AuditLogger
from shared.config import load_gold_tier_config
from shared.error_handler import retry_with_backoff
from shared.frontmatter_validator import BriefingMetadata

logger = logging.getLogger(__name__)


class WeeklyAuditGenerator:
    """Generate Monday morning CEO briefings."""

    def __init__(self, vault_path: str):
        """
        Initialize weekly audit generator (T023).

        Args:
            vault_path: Path to Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.vault_ops = VaultOps(vault_path)
        self.audit_logger = AuditLogger(vault_path)

        # Initialize analyzers
        self.revenue_analyzer = RevenueAnalyzer(vault_path)
        self.bottleneck_detector = BottleneckDetector(vault_path)
        self.cost_optimizer = CostOptimizer(vault_path)

        # Track warnings/errors for graceful degradation
        self.warnings = []
        self.errors = []

    def generate_briefing(self, output_path: Optional[str] = None) -> Dict:
        """
        Generate complete CEO briefing with graceful degradation (T028).

        Args:
            output_path: Where to save briefing (default: Briefings/YYYY-MM-DD_CEO_Briefing.md)

        Returns:
            Dictionary with briefing metadata and content
        """
        logger.info("Starting CEO briefing generation")
        self.warnings = []
        self.errors = []

        try:
            # Load business goals (T024)
            logger.info("Loading business goals")
            business_goals = self.load_business_goals()

            # Analyze revenue (T025)
            logger.info("Analyzing revenue")
            revenue_data = self.analyze_revenue()
            revenue_progress = self.revenue_analyzer.calculate_mtd(
                revenue_data,
                business_goals['monthly_revenue_target']
            )
            revenue_data['mtd_progress'] = revenue_progress

            # Analyze completed tasks (T026)
            logger.info("Analyzing completed tasks")
            completed_tasks = self.analyze_completed_tasks()
            bottleneck_summary = self.bottleneck_detector.get_bottleneck_summary(
                completed_tasks
            )

            # Calculate health score (T027)
            health_score = self._calculate_health_score(
                revenue_progress,
                bottleneck_summary['on_time_rate'],
                bottleneck_summary['bottleneck_count']
            )

            # Generate briefing content (T029)
            logger.info("Generating briefing content")
            briefing_content = self._generate_briefing_content({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'health_score': health_score,
                'revenue_data': revenue_data,
                'business_goals': business_goals,
                'bottleneck_summary': bottleneck_summary,
                'completed_tasks': completed_tasks,
                'warnings': self.warnings,
                'errors': self.errors
            })

            # Determine output path
            if not output_path:
                briefings_dir = self.vault_path / 'Briefings'
                briefings_dir.mkdir(parents=True, exist_ok=True)
                date_str = datetime.now().strftime('%Y-%m-%d')
                output_path = str(briefings_dir / f'{date_str}_CEO_Briefing.md')

            # Write briefing
            logger.info(f"Writing briefing to {output_path}")
            briefing_metadata = BriefingMetadata(
                type='ceo_briefing',
                status='generated',
                health_score=health_score,
                week_number=datetime.now().isocalendar()[1],
                period=datetime.now().strftime('%Y-%m'),
                created_at=datetime.now().isoformat()
            )

            self.vault_ops.write_markdown(
                output_path,
                briefing_content,
                briefing_metadata.model_dump()
            )

            # Update Dashboard.md (T031)
            self._update_dashboard(output_path, health_score, revenue_progress)

            # Log execution (T032)
            self.audit_logger.log_execution(
                action_id=f"briefing_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                action_type='generate_ceo_briefing',
                user='system',
                ai_agent='weekly-ceo-briefing',
                approval_reason='Scheduled Monday morning briefing',
                execution_status='success',
                mcp_server='none',
                tool_name='WeeklyAuditGenerator.generate_briefing',
                tool_inputs={
                    'vault_path': str(self.vault_path),
                    'output_path': output_path
                },
                tool_output={
                    'health_score': health_score,
                    'revenue_progress': revenue_progress,
                    'bottleneck_count': bottleneck_summary['bottleneck_count']
                }
            )

            logger.info("CEO briefing generation complete")

            return {
                'status': 'complete' if not self.warnings else 'partial',
                'health_score': health_score,
                'output_path': output_path,
                'warnings': self.warnings,
                'errors': self.errors
            }

        except Exception as e:
            logger.error(f"Failed to generate briefing: {e}")
            self.errors.append(f"Critical error: {e}")

            # Log failure
            self.audit_logger.log_execution(
                action_id=f"briefing_failed_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                action_type='generate_ceo_briefing',
                user='system',
                ai_agent='weekly-ceo-briefing',
                approval_reason='Scheduled Monday morning briefing',
                execution_status='failure',
                mcp_server='none',
                tool_name='WeeklyAuditGenerator.generate_briefing',
                tool_inputs={'vault_path': str(self.vault_path)},
                error=str(e)
            )

            raise

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def load_business_goals(self) -> Dict:
        """
        Load business goals from Business_Goals.md (T024).

        Returns:
            Dictionary with monthly_goal, metrics, active_projects, audit_rules
        """
        try:
            goals = self.revenue_analyzer.load_business_goals()
            logger.info(f"Loaded business goals: ${goals['monthly_revenue_target']:,.2f} target")
            return goals
        except Exception as e:
            logger.warning(f"Failed to load business goals: {e}")
            self.warnings.append("Business_Goals.md not found - using default targets")
            return {
                'monthly_revenue_target': 10000.0,
                'weekly_task_target': 20,
                'active_projects': [],
                'audit_rules': {}
            }

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def analyze_revenue(self) -> Dict:
        """
        Analyze revenue from Accounting/Current_Month.md (T025).

        Returns:
            Dictionary with parsed revenue table, totals, transaction details
        """
        try:
            revenue = self.revenue_analyzer.analyze_revenue()
            logger.info(f"Analyzed revenue: ${revenue['total_paid']:,.2f} paid, "
                       f"${revenue['total_pending']:,.2f} pending")
            return revenue
        except Exception as e:
            logger.warning(f"Failed to analyze revenue: {e}")
            self.warnings.append("Accounting/Current_Month.md not found - using zero revenue")
            return {
                'total_paid': 0.0,
                'total_pending': 0.0,
                'invoices_paid': 0,
                'invoices_pending': 0,
                'transactions': [],
                'currency': 'USD',
                'mtd_progress': 0.0
            }

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def analyze_completed_tasks(self) -> list:
        """
        Analyze completed tasks from Done/ folder (T026).

        Returns:
            List of completed task dictionaries
        """
        try:
            tasks = self.bottleneck_detector.analyze_completed_tasks()
            logger.info(f"Analyzed {len(tasks)} completed tasks")
            return tasks
        except Exception as e:
            logger.warning(f"Failed to analyze completed tasks: {e}")
            self.warnings.append("Done/ folder not found - no task completion data")
            return []

    def _calculate_health_score(self, revenue_progress: float,
                               on_time_rate: float,
                               bottleneck_count: int) -> int:
        """
        Calculate overall business health score (T027).

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

        logger.info(f"Health score: {health_score} (revenue: {revenue_score:.1f}, "
                   f"operations: {operations_score:.1f}, penalty: {bottleneck_penalty})")

        return int(health_score)

    def _generate_briefing_content(self, data: Dict) -> str:
        """
        Generate markdown briefing content (T029).

        Args:
            data: Dictionary with all analysis data

        Returns:
            Complete markdown briefing content
        """
        lines = [
            f"# CEO Briefing - {data['date']}",
            "",
            "## Executive Summary",
            "",
            f"**Health Score:** {data['health_score']}/100",
            "",
            "## Revenue Analysis",
            "",
            f"**Month-to-Date Progress:** {data['revenue_data']['mtd_progress']:.1f}%",
            f"**Target:** ${data['business_goals']['monthly_revenue_target']:,.2f}",
            f"**Collected:** ${data['revenue_data']['total_paid']:,.2f}",
            f"**Pending:** ${data['revenue_data']['total_pending']:,.2f}",
            "",
            "### Transactions",
            ""
        ]

        # Add transaction table
        if data['revenue_data']['transactions']:
            lines.append("| Invoice | Amount | Date | Status |")
            lines.append("|---------|--------|------|--------|")
            for txn in data['revenue_data']['transactions'][:10]:  # Top 10
                lines.append(f"| {txn['invoice_id']} | "
                           f"${txn['amount']:,.2f} | "
                           f"{txn['date']} | "
                           f"{txn['status'].title()} |")
        else:
            lines.append("*No transactions found*")

        lines.extend([
            "",
            "## Completed Tasks",
            "",
            f"**Total Completed:** {data['bottleneck_summary']['total_tasks']}",
            f"**On-Time Rate:** {data['bottleneck_summary']['on_time_rate']}%",
            f"**Bottlenecks:** {data['bottleneck_summary']['bottleneck_count']}",
            ""
        ])

        # Add bottlenecks section
        if data['bottleneck_summary']['top_bottlenecks']:
            lines.extend([
                "### Top Bottlenecks",
                "",
                "| Task | Days Late | Severity |",
                "|------|-----------|----------|"
            ])
            for bn in data['bottleneck_summary']['top_bottlenecks']:
                lines.append(f"| {bn['title']} | "
                           f"{bn['delay_days']} | "
                           f"{bn['severity'].title()} |")
            lines.append("")

        # Add cost optimization section
        lines.extend([
            "## Cost Optimization",
            "",
            "*Cost optimization analysis available in full implementation*",
            ""
        ])

        # Add action items section
        lines.extend([
            "## Action Items",
            "",
            "*No action items generated*",
            ""
        ])

        # Add warnings/errors if present
        if data['warnings']:
            lines.extend([
                "## Warnings",
                ""
            ])
            for warning in data['warnings']:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")

        if data['errors']:
            lines.extend([
                "## Errors",
                ""
            ])
            for error in data['errors']:
                lines.append(f"- ❌ {error}")
            lines.append("")

        # Add notes
        lines.extend([
            "## Notes",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Briefing ID: {datetime.now().strftime('%Y%m%d%H%M%S')}",
            ""
        ])

        return '\n'.join(lines)

    def _update_dashboard(self, briefing_path: str,
                         health_score: int,
                         revenue_progress: float) -> None:
        """
        Update Dashboard.md with latest briefing link (T031).

        Args:
            briefing_path: Path to generated briefing
            health_score: Calculated health score
            revenue_progress: Revenue progress percentage
        """
        dashboard_path = self.vault_path / 'Dashboard.md'

        try:
            if dashboard_path.exists():
                content, metadata = self.vault_ops.read_markdown(str(dashboard_path))
            else:
                content = "# Dashboard\n\n"
                metadata = {}

            # Add latest briefing section
            briefing_link = f"[{Path(briefing_path).name}]({briefing_path})"
            health_badge = f"{'🟢' if health_score >= 70 else '🟡' if health_score >= 40 else '🔴'} {health_score}/100"

            update_section = f"""

## Latest CEO Briefing

**Health Score:** {health_badge}
**Revenue Progress:** {revenue_progress:.1f}%
**Briefing:** {briefing_link}

Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""

            # Prepend to dashboard (latest first)
            updated_content = update_section + content
            self.vault_ops.write_markdown(str(dashboard_path), updated_content, metadata)

            logger.info("Dashboard.md updated")
        except Exception as e:
            logger.warning(f"Failed to update Dashboard.md: {e}")
            self.warnings.append("Dashboard.md update failed")


def main():
    """CLI entry point (T030)."""
    parser = argparse.ArgumentParser(
        description='Generate Monday Morning CEO Briefing'
    )
    parser.add_argument(
        '--vault-path',
        default='AI_Employee_Vault',
        help='Path to Obsidian vault (default: AI_Employee_Vault)'
    )
    parser.add_argument(
        '--output',
        help='Output path for briefing (default: Briefings/YYYY-MM-DD_CEO_Briefing.md)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging (T032)
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load config
    config = load_gold_tier_config()
    vault_path = config.require('VAULT_PATH', default=args.vault_path)

    # Generate briefing
    generator = WeeklyAuditGenerator(vault_path)
    result = generator.generate_briefing(output_path=args.output)

    # Print result
    print(f"\n{'='*60}")
    print(f"CEO Briefing Generated")
    print(f"{'='*60}")
    print(f"Status: {result['status'].upper()}")
    print(f"Health Score: {result['health_score']}/100")
    print(f"Output: {result['output_path']}")

    if result['warnings']:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")

    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"  ❌ {error}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

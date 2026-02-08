#!/usr/bin/env python3
"""
Weekly CEO Briefing Generator - Monday Morning Business Audit

Analyzes business goals, completed tasks, revenue metrics, bottlenecks,
and cost optimization opportunities. Generates comprehensive briefing.

Created for Gold Tier AI Employee - CEO Briefing Feature
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontmatter import Frontmatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeeklyAuditGenerator:
    """Generate weekly CEO briefing from vault data."""

    def __init__(self, vault_path: str):
        """Initialize audit generator."""
        self.vault_path = Path(vault_path)
        self.briefings_dir = self.vault_path / 'Briefings'
        self.briefings_dir.mkdir(parents=True, exist_ok=True)

        self.data = {
            'business_goals': {},
            'revenue': {},
            'tasks': {},
            'bottlenecks': [],
            'cost_optimizations': [],
            'metrics': {}
        }

    def load_business_goals(self) -> Dict:
        """Load Business_Goals.md and extract targets."""
        goals_file = self.vault_path / 'Business_Goals.md'

        if not goals_file.exists():
            logger.warning("Business_Goals.md not found")
            return {}

        try:
            with open(goals_file, 'r', encoding='utf-8') as f:
                content, fm = Frontmatter.parse(f.read())

            return fm or {}

        except Exception as e:
            logger.error(f"Error loading Business_Goals.md: {e}")
            return {}

    def analyze_revenue(self) -> Dict:
        """Analyze revenue from Accounting/Current_Month.md."""
        accounting_file = self.vault_path / 'Accounting' / 'Current_Month.md'

        revenue_data = {
            'total': 0,
            'sources': [],
            'mtd': 0,
            'entries': []
        }

        if not accounting_file.exists():
            logger.warning("Accounting/Current_Month.md not found")
            return revenue_data

        try:
            with open(accounting_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse revenue entries (simplified - would use regex in production)
            lines = content.split('\n')
            for line in lines:
                if '|' in line and '$' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        try:
                            amount_str = parts[2].replace('$', '').replace(',', '').strip()
                            amount = float(amount_str)
                            revenue_data['entries'].append({
                                'date': parts[0],
                                'source': parts[1],
                                'amount': amount,
                                'notes': parts[3] if len(parts) > 3 else ''
                            })
                            revenue_data['total'] += amount
                        except (ValueError, IndexError):
                            continue

            revenue_data['mtd'] = revenue_data['total']

        except Exception as e:
            logger.error(f"Error analyzing revenue: {e}")

        return revenue_data

    def analyze_completed_tasks(self) -> Dict:
        """Analyze completed tasks from Tasks/Done/."""
        done_dir = self.vault_path / 'Tasks' / 'Done'

        task_data = {
            'total': 0,
            'on_time': 0,
            'overdue': 0,
            'tasks': []
        }

        if not done_dir.exists():
            return task_data

        try:
            for task_file in done_dir.glob('*.md'):
                with open(task_file, 'r', encoding='utf-8') as f:
                    content, fm = Frontmatter.parse(f.read())

                if fm:
                    task_data['total'] += 1

                    # Check if completed on time
                    completed_at = fm.get('completed_at')
                    due_date = fm.get('due_date')

                    if completed_at and due_date:
                        if completed_at <= due_date:
                            task_data['on_time'] += 1
                        else:
                            task_data['overdue'] += 1

                    task_data['tasks'].append({
                        'title': fm.get('title', task_file.stem),
                        'completed_at': completed_at,
                        'due_date': due_date
                    })

        except Exception as e:
            logger.error(f"Error analyzing tasks: {e}")

        return task_data

    def detect_bottlenecks(self) -> List[Dict]:
        """Detect bottlenecks from overdue tasks and delays."""
        bottlenecks = []
        done_dir = self.vault_path / 'Tasks' / 'Done'

        if not done_dir.exists():
            return bottlenecks

        try:
            for task_file in done_dir.glob('*.md'):
                with open(task_file, 'r', encoding='utf-8') as f:
                    content, fm = Frontmatter.parse(f.read())

                if fm:
                    completed_at = fm.get('completed_at')
                    due_date = fm.get('due_date')

                    # Calculate delay
                    if completed_at and due_date:
                        try:
                            if isinstance(completed_at, str):
                                completed_dt = datetime.fromisoformat(completed_at.replace('Z', ''))
                            else:
                                completed_dt = completed_at

                            if isinstance(due_date, str):
                                due_dt = datetime.fromisoformat(due_date.replace('Z', ''))
                            else:
                                due_dt = due_date

                            if completed_dt > due_dt:
                                delay_days = (completed_dt - due_dt).days

                                if delay_days > 0:
                                    bottlenecks.append({
                                        'task': fm.get('title', task_file.stem),
                                        'expected': due_date,
                                        'actual': completed_at,
                                        'delay_days': delay_days,
                                        'severity': 'HIGH' if delay_days > 3 else 'MEDIUM'
                                    })
                        except (ValueError, TypeError):
                            continue

            # Sort by delay days (descending)
            bottlenecks.sort(key=lambda x: x['delay_days'], reverse=True)

        except Exception as e:
            logger.error(f"Error detecting bottlenecks: {e}")

        return bottlenecks[:5]  # Return top 5

    def generate_briefing(self) -> Path:
        """Generate CEO briefing document."""
        logger.info("Generating weekly CEO briefing...")

        # Load all data
        self.data['business_goals'] = self.load_business_goals()
        self.data['revenue'] = self.analyze_revenue()
        self.data['tasks'] = self.analyze_completed_tasks()
        self.data['bottlenecks'] = self.detect_bottlenecks()

        # Calculate metrics
        total_tasks = self.data['tasks'].get('total', 0)
        on_time_tasks = self.data['tasks'].get('on_time', 0)
        on_time_rate = (on_time_tasks / total_tasks * 100) if total_tasks > 0 else 0

        revenue = self.data['revenue'].get('total', 0)
        revenue_target = self.data['business_goals'].get('monthly_goal', 10000)
        revenue_progress = (revenue / revenue_target * 100) if revenue_target > 0 else 0

        # Generate briefing content
        briefing_content = self._generate_briefing_content(
            revenue=revenue,
            revenue_progress=revenue_progress,
            on_time_rate=on_time_rate,
            bottlenecks=self.data['bottlenecks']
        )

        # Save briefing
        today = datetime.now()
        briefing_file = self.briefings_dir / f"{today.strftime('%Y-%m-%d')}_Monday_Briefing.md"

        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing_content)

        logger.info(f"Briefing generated: {briefing_file}")
        return briefing_file

    def _generate_briefing_content(self, revenue: float, revenue_progress: float,
                                   on_time_rate: float, bottlenecks: List[Dict]) -> str:
        """Generate briefing markdown content."""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())

        # Calculate health score
        health_score = self._calculate_health_score(revenue_progress, on_time_rate, len(bottlenecks))

        content = f"""---
generated: {today.isoformat()}Z
period: {week_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}
week_number: {today.isocalendar()[1]}
---

# Monday Morning CEO Briefing - Week of {today.strftime('%B %d, %Y')}

## Executive Summary

{'Strong week with revenue tracking well.' if revenue_progress > 40 else 'Revenue needs attention this week.'}

**Overall Status**: {'🟢 On Track' if health_score >= 80 else '🟡 Needs Attention' if health_score >= 60 else '🔴 Critical'}

---

## Revenue

### This Week
- **Total**: ${revenue:,.2f}
- **Sources**: {len(self.data['revenue'].get('entries', []))} transactions
- **Target**: ${self.data['business_goals'].get('monthly_goal', 10000):,.2f}

### Month-to-Date
- **Current**: ${revenue:,.2f} ({revenue_progress:.1f}% of target)
- **Trend**: {'✅ On track' if revenue_progress >= 40 else '⚠️ Behind target'}

### Revenue Sources
"""

        # Add revenue entries
        for entry in self.data['revenue'].get('entries', [])[:10]:
            content += f"- {entry.get('date', 'N/A')}: {entry.get('source', 'Unknown')} - ${entry.get('amount', 0):,.2f}\n"

        content += f"""
---

## Completed Tasks

### This Week's Performance
- **Total Completed**: {self.data['tasks'].get('total', 0)} tasks
- **On-Time Rate**: {on_time_rate:.1f}%
- **Overdue**: {self.data['tasks'].get('overdue', 0)} tasks

---

## Bottlenecks
"""

        if bottlenecks:
            content += "\n| Task | Delay | Severity |\n|------|-------|----------|\n"
            for b in bottlenecks:
                content += f"| {b.get('task')} | +{b.get('delay_days')} days | {b.get('severity')} |\n"
        else:
            content += "\n✅ No significant bottlenecks detected this week.\n"

        content += f"""
---

## Health Score: {health_score}/100

**Breakdown**:
- Revenue: {min(100, revenue_progress):.0f}/100
- Operations: {min(100, on_time_rate):.0f}/100
- Bottlenecks: {max(0, 100 - len(bottlenecks) * 10):.0f}/100

---

## Action Items

### Review This Week
"""

        # Add action items based on bottlenecks
        if bottlenecks:
            content += "- [ ] Address critical bottlenecks (see above)\n"

        if revenue_progress < 40:
            content += "- [ ] Focus on revenue-generating activities\n"

        if on_time_rate < 80:
            content += "- [ ] Review task estimation accuracy\n"

        content += f"""
- [ ] Review upcoming deadlines
- [ ] Update Business_Goals.md if needed

---

## Notes

Generated by AI Employee v1.0 (Gold Tier)
Report Period: {week_start.strftime('%B %d, %Y')} - {today.strftime('%B %d, %Y')}
Next Briefing: {(today + timedelta(days=7)).strftime('%B %d, %Y')}
"""

        return content

    def _calculate_health_score(self, revenue_progress: float, on_time_rate: float,
                               bottleneck_count: int) -> int:
        """Calculate overall business health score."""
        # Weighted components
        revenue_score = min(100, revenue_progress)
        operations_score = min(100, on_time_rate)
        bottleneck_penalty = bottleneck_count * 10

        # Calculate weighted average
        health_score = (revenue_score * 0.5 + operations_score * 0.5)
        health_score = max(0, health_score - bottleneck_penalty)

        return int(health_score)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate weekly CEO briefing')
    parser.add_argument('--vault-path', required=True, help='Path to Obsidian vault')
    parser.add_argument('--output', help='Output file path (optional)')
    args = parser.parse_args()

    generator = WeeklyAuditGenerator(args.vault_path)
    briefing_file = generator.generate_briefing()

    if args.output:
        import shutil
        shutil.copy(briefing_file, args.output)
        logger.info(f"Briefing copied to: {args.output}")

    logger.info("CEO briefing generation complete!")


if __name__ == '__main__':
    main()

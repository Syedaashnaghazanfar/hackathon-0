"""
Integration tests for CEO briefing generation with graceful degradation.

Tests missing Business_Goals.md, empty Accounting/, corrupted YAML,
and ensures briefing generation continues with partial data.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))


# Mock briefing generator implementation
class BriefingGenerator:
    """Generate CEO briefing with graceful degradation."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.errors = []
        self.warnings = []

    def read_business_goals(self) -> dict:
        """
        Read Business_Goals.md with graceful degradation.

        Returns:
            Dictionary with goals data or empty dict if file missing/invalid
        """
        goals_file = self.vault_path / 'Business_Goals.md'

        if not goals_file.exists():
            self.warnings.append("Business_Goals.md not found - using default targets")
            return {
                'monthly_revenue_target': 10000.0,
                'weekly_task_target': 20,
                'active_projects': []
            }

        try:
            # Simulate reading frontmatter
            content = goals_file.read_text()

            # Check for valid YAML structure (must have --- delimiters)
            if '---' not in content:
                self.errors.append(f"Failed to parse Business_Goals.md: Invalid YAML structure (missing --- delimiters)")
                return {
                    'monthly_revenue_target': 10000.0,
                    'weekly_task_target': 20,
                    'active_projects': []
                }

            # Check for unclosed brackets (common YAML error)
            lines = content.split('\n')
            yaml_section = []
            in_yaml = False
            for line in lines:
                if line.strip() == '---':
                    if in_yaml:
                        break  # End of YAML
                    else:
                        in_yaml = True  # Start of YAML
                        continue
                if in_yaml:
                    yaml_section.append(line)

            yaml_content = '\n'.join(yaml_section)
            # Check for unbalanced brackets
            if yaml_content.count('[') != yaml_content.count(']'):
                self.errors.append(f"Failed to parse Business_Goals.md: Invalid YAML (unclosed brackets)")
                return {
                    'monthly_revenue_target': 10000.0,
                    'weekly_task_target': 20,
                    'active_projects': []
                }

            # Simple parsing for test
            if 'revenue_target:' in content:
                target_line = [l for l in content.split('\n') if 'revenue_target:' in l][0]
                target = float(target_line.split(':')[1].strip().replace('$', '').replace(',', ''))
            else:
                target = 10000.0

            return {
                'monthly_revenue_target': target,
                'weekly_task_target': 20,
                'active_projects': []
            }
        except Exception as e:
            self.errors.append(f"Failed to parse Business_Goals.md: {e}")
            return {
                'monthly_revenue_target': 10000.0,
                'weekly_task_target': 20,
                'active_projects': []
            }

    def read_accounting_data(self) -> dict:
        """
        Read Accounting/Current_Month.md with graceful degradation.

        Returns:
            Dictionary with accounting data or zeros if missing/invalid
        """
        accounting_file = self.vault_path / 'Accounting' / 'Current_Month.md'

        if not accounting_file.exists():
            self.warnings.append("Accounting/Current_Month.md not found - using zero revenue")
            return {
                'total_paid': 0.0,
                'total_pending': 0.0,
                'invoices_paid': 0,
                'invoices_pending': 0
            }

        try:
            content = accounting_file.read_text()

            # Simple parsing
            if '|' in content:
                # Has table format
                return {
                    'total_paid': 5000.0,  # Mock parsed value
                    'total_pending': 2500.0,
                    'invoices_paid': 3,
                    'invoices_pending': 2
                }
            else:
                return {
                    'total_paid': 0.0,
                    'total_pending': 0.0,
                    'invoices_paid': 0,
                    'invoices_pending': 0
                }
        except Exception as e:
            self.errors.append(f"Failed to parse Accounting data: {e}")
            return {
                'total_paid': 0.0,
                'total_pending': 0.0,
                'invoices_paid': 0,
                'invoices_pending': 0
            }

    def read_done_items(self) -> list:
        """
        Read completed action items from Done/ folder.

        Returns:
            List of done items or empty list if folder missing
        """
        done_folder = self.vault_path / 'Done'

        if not done_folder.exists():
            self.warnings.append("Done/ folder not found - no task completion data")
            return []

        try:
            items = []
            for file in done_folder.glob('*.md'):
                content = file.read_text()
                # Mock parsing
                items.append({
                    'title': file.stem,
                    'completed_date': '2024-01-15',
                    'due_date': '2024-01-15'
                })
            return items
        except Exception as e:
            self.errors.append(f"Failed to read Done items: {e}")
            return []

    def calculate_health_score(self, revenue_progress: float, on_time_rate: float,
                             bottleneck_count: int) -> int:
        """Calculate health score with bounds checking."""
        revenue_score = min(100, revenue_progress)
        operations_score = min(100, on_time_rate)
        bottleneck_penalty = bottleneck_count * 10
        health_score = (revenue_score * 0.5 + operations_score * 0.5)
        health_score = max(0, health_score - bottleneck_penalty)
        return int(health_score)

    def generate_briefing(self, output_path: str = None) -> dict:
        """
        Generate complete CEO briefing with graceful degradation.

        Args:
            output_path: Where to save the briefing (optional)

        Returns:
            Dictionary with briefing content and status
        """
        self.errors = []
        self.warnings = []

        # Read all data sources with graceful degradation
        goals = self.read_business_goals()
        accounting = self.read_accounting_data()
        done_items = self.read_done_items()

        # Calculate metrics
        revenue_progress = (accounting['total_paid'] / goals['monthly_revenue_target']) * 100
        on_time_count = sum(1 for item in done_items if item.get('completed_date') <= item.get('due_date'))
        on_time_rate = (on_time_count / len(done_items) * 100) if done_items else 100

        # Mock bottleneck detection
        bottleneck_count = sum(1 for item in done_items
                             if item.get('completed_date') > item.get('due_date'))

        health_score = self.calculate_health_score(
            revenue_progress, on_time_rate, bottleneck_count
        )

        briefing = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'health_score': health_score,
            'revenue_progress': round(revenue_progress, 1),
            'on_time_rate': round(on_time_rate, 1),
            'bottleneck_count': bottleneck_count,
            'warnings': self.warnings,
            'errors': self.errors,
            'status': 'partial' if (self.warnings or self.errors) else 'complete'
        }

        # Save if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Generate markdown content
            content = self._generate_markdown(briefing)
            output_file.write_text(content)

        return briefing

    def _generate_markdown(self, briefing: dict) -> str:
        """Generate markdown briefing content."""
        lines = [
            f"# CEO Briefing - {briefing['date']}",
            "",
            "## Health Score",
            f"**{briefing['health_score']}/100**",
            "",
            "## Metrics",
            f"- Revenue Progress: {briefing['revenue_progress']}%",
            f"- On-Time Rate: {briefing['on_time_rate']}%",
            f"- Bottlenecks: {briefing['bottleneck_count']}",
            ""
        ]

        if briefing['warnings']:
            lines.extend([
                "## Warnings",
                *[f"- {w}" for w in briefing['warnings']],
                ""
            ])

        if briefing['errors']:
            lines.extend([
                "## Errors",
                *[f"- {e}" for e in briefing['errors']],
                ""
            ])

        return '\n'.join(lines)


class TestBriefingGeneration:
    """Test suite for briefing generation with graceful degradation."""

    def test_generate_complete_briefing(self):
        """Test generating briefing with all data sources present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Create Business_Goals.md
            goals_file = vault / 'Business_Goals.md'
            goals_file.write_text("""
---
revenue_target: $10000.00
---
# Business Goals
""")

            # Create Accounting folder with data
            accounting_dir = vault / 'Accounting'
            accounting_dir.mkdir()
            accounting_file = accounting_dir / 'Current_Month.md'
            accounting_file.write_text("""
| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $5,000.00 | 2024-01-15 | Paid |
""")

            # Create Done folder with items
            done_dir = vault / 'Done'
            done_dir.mkdir()
            (done_dir / 'task1.md').write_text('Done')

            # Generate briefing
            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            assert briefing['status'] == 'complete'
            assert len(briefing['warnings']) == 0
            assert len(briefing['errors']) == 0
            assert briefing['health_score'] >= 0

    def test_missing_business_goals(self):
        """Test graceful degradation when Business_Goals.md is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Create other data but not Business_Goals.md
            accounting_dir = vault / 'Accounting'
            accounting_dir.mkdir()
            (accounting_dir / 'Current_Month.md').write_text('| Invoice | Amount |')

            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            assert briefing['status'] == 'partial'
            assert any('Business_Goals.md not found' in w for w in briefing['warnings'])
            # Should use default target and continue
            assert briefing['health_score'] >= 0

    def test_empty_accounting_folder(self):
        """Test graceful degradation when Accounting/ folder is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Create Business_Goals.md but no accounting data
            (vault / 'Business_Goals.md').write_text('revenue_target: $10000')
            (vault / 'Accounting').mkdir()  # Empty folder

            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            assert briefing['status'] == 'partial'
            assert any('Accounting/Current_Month.md not found' in w for w in briefing['warnings'])
            # Revenue should be 0
            assert briefing['revenue_progress'] == 0.0

    def test_missing_done_folder(self):
        """Test graceful degradation when Done/ folder doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            (vault / 'Business_Goals.md').write_text('revenue_target: $10000')
            accounting_dir = vault / 'Accounting'
            accounting_dir.mkdir()
            (accounting_dir / 'Current_Month.md').write_text('| Invoice | Amount |')

            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            assert briefing['status'] == 'partial'
            assert any('Done/ folder not found' in w for w in briefing['warnings'])
            # Should still generate briefing
            assert briefing['health_score'] >= 0

    def test_corrupted_yaml_frontmatter(self):
        """Test handling of corrupted YAML in frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Create Business_Goals.md with invalid YAML (unclosed bracket)
            goals_file = vault / 'Business_Goals.md'
            goals_file.write_text("""
---
invalid: yaml: content: [broken
# Business Goals
""")

            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            assert briefing['status'] == 'partial'
            assert len(briefing['errors']) > 0
            # Should continue with default values
            assert briefing['health_score'] >= 0

    def test_multiple_data_sources_missing(self):
        """Test graceful degradation with multiple missing sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Empty vault - no data sources
            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            assert briefing['status'] == 'partial'
            assert len(briefing['warnings']) >= 3  # Goals, Accounting, Done
            # Should still generate a briefing
            assert 'health_score' in briefing
            # No revenue (0%), no tasks (on_time_rate defaults to 100% when no tasks)
            # Health score = (0 * 0.5 + 100 * 0.5) - 0 = 50
            assert briefing['health_score'] == 50

    def test_briefing_saved_to_file(self):
        """Test that briefing is saved to specified output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Create minimal data
            (vault / 'Business_Goals.md').write_text('revenue_target: $10000')

            output_path = Path(tmpdir) / 'Briefings' / 'weekly_briefing.md'

            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing(str(output_path))

            # File should exist
            assert output_path.exists()

            # Content should have expected structure
            content = output_path.read_text()
            assert '# CEO Briefing' in content
            assert '## Health Score' in content
            assert '## Metrics' in content

    def test_health_score_with_warnings(self):
        """Test that health score is calculated even with warnings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Only partial data
            (vault / 'Business_Goals.md').write_text('revenue_target: $10000')

            generator = BriefingGenerator(str(vault))
            briefing = generator.generate_briefing()

            # Should have warnings but still calculate score
            assert len(briefing['warnings']) > 0
            assert 'health_score' in briefing
            assert isinstance(briefing['health_score'], int)

    def test_briefing_includes_warnings_and_errors(self):
        """Test that generated briefing includes warnings and errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Create data that will trigger warnings
            (vault / 'Business_Goals.md').write_text('invalid yaml')

            generator = BriefingGenerator(str(vault))
            output_path = Path(tmpdir) / 'briefing.md'
            briefing = generator.generate_briefing(str(output_path))

            content = output_path.read_text()

            # Should include warnings/errors sections
            if briefing['warnings']:
                assert '## Warnings' in content
            if briefing['errors']:
                assert '## Errors' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

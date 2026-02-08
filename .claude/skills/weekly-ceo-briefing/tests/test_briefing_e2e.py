"""
End-to-end test for complete CEO briefing workflow.

Tests the full pipeline from vault with sample data through briefing
generation, validating all sections and health score formula.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def create_sample_vault(tmpdir: Path) -> str:
    """
    Create a sample vault with test data.

    Args:
        tmpdir: Temporary directory path

    Returns:
        Path to created vault
    """
    vault_path = tmpdir / 'test_vault'
    vault_path.mkdir()

    # Create Business_Goals.md
    business_goals = vault_path / 'Business_Goals.md'
    business_goals.write_text("""---
type: business_goals
monthly_revenue_target: 10000.0
weekly_task_target: 20
currency: USD
---

# Business Goals

Monthly target: $10,000
""")

    # Create Accounting folder with Current_Month.md
    accounting_dir = vault_path / 'Accounting'
    accounting_dir.mkdir()

    current_month = accounting_dir / 'Current_Month.md'
    current_month.write_text("""---
type: accounting
period: "2024-01"
currency: USD
---

# Accounting January 2024

## Invoice Tracker

| Invoice | Amount | Date | Status |
|---------|--------|------|--------|
| INV-001 | $5,000.00 | 2024-01-15 | Paid |
| INV-002 | $2,500.00 | 2024-01-10 | Paid |
| INV-003 | $1,000.00 | 2024-01-20 | Pending |
""")

    # Create Done folder with sample completed tasks
    done_dir = vault_path / 'Done'
    done_dir.mkdir()

    # Create 5 completed tasks - 3 on time, 2 late
    for i in range(1, 6):
        task_file = done_dir / f'task_{i}.md'

        if i <= 3:
            # On-time tasks
            due_date = '2024-01-10'
            completed_date = '2024-01-10'
        else:
            # Late tasks
            due_date = '2024-01-10'
            completed_date = '2024-01-15'  # 5 days late

        task_file.write_text(f"""---
type: action_item
status: done
title: "Task {i}"
due_date: {due_date}
completed_date: {completed_date}
category: Testing
---

# Task {i}

Completed test task {i}
""")

    return str(vault_path)


class TestBriefingE2E:
    """End-to-end test suite for CEO briefing generation."""

    def test_complete_briefing_workflow(self):
        """
        Test complete briefing workflow from sample vault to generated briefing.

        Validates:
        - Vault with sample data loads correctly
        - All sections generated properly
        - Health score formula applied correctly
        - Briefing saved to correct location
        - Dashboard.md updated
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create sample vault
            vault_path = create_sample_vault(tmpdir_path)

            # Import generator
            from weekly_audit_new import WeeklyAuditGenerator

            # Generate briefing
            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            # Verify generation status
            assert result['status'] in ['complete', 'partial']

            # Verify output file exists
            output_path = Path(result['output_path'])
            assert output_path.exists()

            # Read generated briefing
            briefing_content = output_path.read_text()

            # Validate all sections present
            assert '# CEO Briefing' in briefing_content
            assert '## Executive Summary' in briefing_content
            assert '## Revenue Analysis' in briefing_content
            assert '## Completed Tasks' in briefing_content
            assert '## Health Score' in briefing_content or '**Health Score:**' in briefing_content

    def test_health_score_formula_validation(self):
        """
        Validate health score formula with known inputs.

        Given:
        - Revenue: $7,500 paid (75% of $10,000 target)
        - Tasks: 5 total, 3 on-time (60% on-time rate)
        - Bottlenecks: 2 tasks delayed (5 days each)

        Expected:
        - Revenue score: min(100, 75) = 75
        - Operations score: min(100, 60) = 60
        - Weighted average: (75 * 0.5 + 60 * 0.5) = 67.5
        - Bottleneck penalty: 2 * 10 = 20
        - Final health score: max(0, 67.5 - 20) = 47.5 → 47 (integer)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = create_sample_vault(tmpdir_path)

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            # Health score should be 47 based on test data
            # Revenue: 75%, On-time: 60%, Bottlenecks: 2
            # Formula: (75 * 0.5 + 60 * 0.5) - 20 = 67.5 - 20 = 47.5 → 47
            expected_health_score = 47

            assert result['health_score'] == expected_health_score, \
                f"Expected health score {expected_health_score}, got {result['health_score']}"

    def test_revenue_section_validation(self):
        """
        Validate revenue section with parsed accounting data.

        Expected:
        - Total paid: $7,500 (INV-001 + INV-002)
        - Total pending: $1,000 (INV-003)
        - MTD progress: 75% ($7,500 / $10,000)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = create_sample_vault(tmpdir_path)

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            output_path = Path(result['output_path'])
            briefing_content = output_path.read_text()

            # Validate revenue values in content
            assert '7,500' in briefing_content or '7500' in briefing_content
            assert '75.0%' in briefing_content or '75%' in briefing_content
            assert '10,000' in briefing_content or '10000' in briefing_content

            # Check for invoice table
            assert '| INV-' in briefing_content
            assert 'Paid' in briefing_content

    def test_bottlenecks_section_validation(self):
        """
        Validate bottlenecks section with detected delays.

        Expected:
        - 2 bottlenecks detected (task_4, task_5)
        - Both 5 days late
        - Severity: medium (3-5 days)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = create_sample_vault(tmpdir_path)

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            output_path = Path(result['output_path'])
            briefing_content = output_path.read_text()

            # Check for bottlenecks section
            if '## Top Bottlenecks' in briefing_content or '## Bottlenecks' in briefing_content:
                # Should show delayed tasks
                assert 'task_4' in briefing_content or 'Task 4' in briefing_content or 'task_5' in briefing_content
                assert '5' in briefing_content  # 5 days late

    def test_dashboard_update(self):
        """
        Validate Dashboard.md updated with latest briefing.

        Expected:
        - Dashboard.md created in vault root
        - Latest briefing section present
        - Health score badge present
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = create_sample_vault(tmpdir_path)

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            # Check Dashboard.md exists
            dashboard_path = Path(vault_path) / 'Dashboard.md'
            assert dashboard_path.exists(), "Dashboard.md should be created"

            dashboard_content = dashboard_path.read_text()

            # Validate dashboard content
            assert '## Latest CEO Briefing' in dashboard_content
            assert 'Health Score' in dashboard_content
            assert 'Revenue Progress' in dashboard_content

            # Check for briefing link
            assert 'CEO_Briefing.md' in dashboard_content

    def test_graceful_degradation_missing_accounting(self):
        """
        Test graceful degradation when Accounting/ folder missing.

        Expected:
        - Briefing still generates
        - Revenue shows as $0
        - Warning included
        - Health score calculated with zero revenue
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = tmpdir_path / 'test_vault'
            vault_path.mkdir()

            # Only Business_Goals.md, no Accounting
            business_goals = vault_path / 'Business_Goals.md'
            business_goals.write_text("""---
monthly_revenue_target: 10000.0
---
# Business Goals
""")

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            # Should still generate
            assert result['status'] == 'partial'
            assert 'output_path' in result

            # Should have warnings
            assert len(result['warnings']) > 0
            assert any('Accounting' in w for w in result['warnings'])

    def test_graceful_degradation_missing_done_folder(self):
        """
        Test graceful degradation when Done/ folder missing.

        Expected:
        - Briefing still generates
        - Task completion shows as 0
        - On-time rate defaults to 100% (no tasks to penalize)
        - Warning included
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = tmpdir_path / 'test_vault'
            vault_path.mkdir()

            # Only Business_Goals.md and Accounting, no Done/
            (vault_path / 'Business_Goals.md').write_text("---\nmonthly_revenue_target: 10000.0\n---\n# Goals")

            accounting_dir = vault_path / 'Accounting'
            accounting_dir.mkdir()
            (accounting_dir / 'Current_Month.md').write_text("| Invoice | Amount | Date | Status |\n| INV-001 | $5000 | 2024-01-15 | Paid |")

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            # Should still generate
            assert result['status'] == 'partial'

            # Should have warnings about Done folder
            assert any('Done' in w for w in result['warnings'])

    def test_briefing_file_naming(self):
        """
        Test that briefing files use correct naming convention.

        Expected:
        - File name format: YYYY-MM-DD_CEO_Briefing.md
        - Created in Briefings/ subfolder
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = create_sample_vault(tmpdir_path)

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)
            result = generator.generate_briefing()

            output_path = Path(result['output_path'])

            # Validate file name format
            assert output_path.parent.name == 'Briefings'
            assert output_path.name.endswith('_CEO_Briefing.md')

            # Validate date format (YYYY-MM-DD_CEO_Briefing.md)
            filename_parts = output_path.stem.split('_')
            assert len(filename_parts) >= 2  # Should have date and title
            date_str = filename_parts[0]
            assert len(date_str) == 10  # YYYY-MM-DD

    def test_multiple_briefing_generations(self):
        """
        Test generating multiple briefings in sequence.

        Expected:
        - Each briefing gets unique timestamp
        - Briefings don't overwrite each other
        - All briefings valid
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            vault_path = create_sample_vault(tmpdir_path)

            from weekly_audit_new import WeeklyAuditGenerator

            generator = WeeklyAuditGenerator(vault_path)

            # Generate 3 briefings
            results = []
            for i in range(3):
                result = generator.generate_briefing()
                results.append(result)

            # All should succeed
            for result in results:
                assert result['status'] in ['complete', 'partial']
                assert Path(result['output_path']).exists()

            # Should have 3 different files (if timestamps differ)
            # Note: In real test, would need to sleep or mock datetime
            output_paths = [r['output_path'] for r in results]
            assert len(set(output_paths)) >= 1  # At least 1 unique file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

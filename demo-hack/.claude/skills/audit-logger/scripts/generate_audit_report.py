#!/usr/bin/env python3
"""Generate audit report from audit logs."""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def generate_report(period='month'):
    """Generate audit report for specified period."""
    if not Path('logs/audit.log').exists():
        print("No audit log found.")
        return

    stats = {
        'total_events': 0,
        'by_event_type': defaultdict(int),
        'by_action_type': defaultdict(int),
        'approvals': {'approved': 0, 'rejected': 0},
        'executions': {'success': 0, 'failed': 0},
        'approval_times': [],
        'execution_times': [],
        'errors': defaultdict(int),
    }

    try:
        with open('logs/audit.log', 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    stats['total_events'] += 1

                    event_type = entry.get('event_type')
                    action_type = entry.get('action_type')

                    stats['by_event_type'][event_type] += 1
                    stats['by_action_type'][action_type] += 1

                    # Approval stats
                    if event_type == 'action_approved':
                        stats['approvals']['approved'] += 1
                        duration = entry.get('approval_info', {}).get('approval_duration_seconds', 0)
                        stats['approval_times'].append(duration)

                    elif event_type == 'action_rejected':
                        stats['approvals']['rejected'] += 1

                    # Execution stats
                    elif event_type == 'action_executed':
                        stats['executions']['success'] += 1
                        exec_time = entry.get('execution_info', {}).get('execution_time_ms', 0)
                        stats['execution_times'].append(exec_time)

                    elif event_type == 'action_failed':
                        stats['executions']['failed'] += 1
                        error = entry.get('execution_info', {}).get('error_type')
                        if error:
                            stats['errors'][error] += 1

                except json.JSONDecodeError:
                    pass

    except FileNotFoundError:
        print("Error reading audit log")
        return

    # Print report
    print("\n" + "=" * 70)
    print(f"AUDIT REPORT - {period.upper()}")
    print("=" * 70 + "\n")

    print(f"Total Events: {stats['total_events']}")

    print(f"\nApprovals:")
    print(f"  ✅ Approved: {stats['approvals']['approved']}")
    print(f"  ❌ Rejected: {stats['approvals']['rejected']}")

    if stats['approval_times']:
        avg_approval = sum(stats['approval_times']) / len(stats['approval_times'])
        print(f"  Average Approval Time: {avg_approval:.1f} seconds ({avg_approval/60:.1f} minutes)")

    print(f"\nExecutions:")
    print(f"  ✅ Successful: {stats['executions']['success']}")
    print(f"  ❌ Failed: {stats['executions']['failed']}")

    if stats['executions']['success'] + stats['executions']['failed'] > 0:
        success_rate = (stats['executions']['success'] /
                       (stats['executions']['success'] + stats['executions']['failed'])) * 100
        print(f"  Success Rate: {success_rate:.1f}%")

    if stats['execution_times']:
        avg_exec = sum(stats['execution_times']) / len(stats['execution_times'])
        print(f"  Average Execution Time: {avg_exec:.1f}ms")

    if stats['errors']:
        print(f"\nErrors:")
        for error_type, count in sorted(stats['errors'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {error_type}: {count}")

    print(f"\nActions by Type:")
    for action_type, count in sorted(stats['by_action_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {action_type}: {count}")

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    import sys
    period = sys.argv[1] if len(sys.argv) > 1 else 'month'
    generate_report(period)

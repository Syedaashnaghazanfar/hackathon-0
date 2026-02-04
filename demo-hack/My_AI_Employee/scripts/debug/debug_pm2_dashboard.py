#!/usr/bin/env python3
"""
Test script for PM2 dashboard integration.

Demonstrates the PM2 status querying feature added to dashboard_updater.py.
This matches the reference-silver implementation.

Usage:
    python test_pm2_dashboard.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from vault_ops.dashboard_updater import DashboardUpdater, update_watcher_status


def test_pm2_query():
    """Test PM2 status querying."""
    print("=" * 60)
    print("Testing PM2 Status Querying")
    print("=" * 60)

    vault_path = Path(__file__).parent / "AI_Employee_Vault"

    if not vault_path.exists():
        print(f"❌ Vault not found at: {vault_path}")
        return

    print(f"✅ Vault found at: {vault_path}\n")

    # Create dashboard updater
    updater = DashboardUpdater(vault_path)

    # Query PM2 for watcher statuses
    print("Querying PM2 for watcher statuses...")
    pm2_statuses = updater.get_pm2_watcher_statuses()

    if not pm2_statuses:
        print("⚠️  No PM2 processes found or PM2 not available")
        print("   Make sure PM2 is installed and watchers are running:")
        print("   - pm2 start ecosystem.config.js")
        print("   - pm2 status")
        return

    print(f"✅ Found {len(pm2_statuses)} PM2 processes\n")

    # Display PM2 status for each watcher
    for watcher_type, data in pm2_statuses.items():
        print(f"📊 {watcher_type.upper()} Watcher:")
        print(f"   Status: {data['status']} (PM2: {data['pm2_status']})")
        print(f"   Uptime: {data['uptime_display']}")
        print(f"   Restarts: {data['restart_count']}")
        print(f"   Stability: {data['stability_label']}")
        print(f"   Memory: {data['memory_mb']} MB")
        print(f"   CPU: {data['cpu_percent']}%")
        print(f"   PM2 ID: {data['pm2_id']}")
        print()

    # Update dashboard with PM2 data
    print("Updating dashboard with PM2 data...")
    update_watcher_status(vault_path, use_pm2=True)
    print("✅ Dashboard updated successfully")

    # Show dashboard summary
    summary = updater.get_dashboard_summary()
    print("\n📋 Dashboard Summary:")
    print(f"   Pending items: {summary['pending_count']}")
    print(f"   Warnings: {summary['warning_count']}")
    print(f"   Recent activities: {summary['activity_count']}")
    print(f"   Dashboard path: {summary['dashboard_path']}")


def test_manual_status():
    """Test manual status update (fallback mode)."""
    print("\n" + "=" * 60)
    print("Testing Manual Status Update (Fallback)")
    print("=" * 60)

    vault_path = Path(__file__).parent / "AI_Employee_Vault"

    if not vault_path.exists():
        print(f"❌ Vault not found at: {vault_path}")
        return

    print("Updating dashboard with manual status...")
    update_watcher_status(
        vault_path,
        gmail_status="running",
        linkedin_status="stopped",
        whatsapp_status="error",
        use_pm2=False  # Disable PM2 querying
    )
    print("✅ Dashboard updated with manual status")


if __name__ == "__main__":
    print("\n🚀 PM2 Dashboard Integration Test\n")

    # Test PM2 querying
    test_pm2_query()

    # Test manual status (fallback)
    test_manual_status()

    print("\n" + "=" * 60)
    print("✅ All tests completed")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start watchers with PM2: cd My_AI_Employee && pm2 start ecosystem.config.js")
    print("2. Check PM2 status: pm2 status")
    print("3. View dashboard: cat AI_Employee_Vault/Dashboard.md")
    print("4. Monitor PM2 logs: pm2 logs")

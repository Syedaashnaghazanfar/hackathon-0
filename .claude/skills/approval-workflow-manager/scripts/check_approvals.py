#!/usr/bin/env python3
"""Check and report pending approvals."""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_pending_approvals():
    """Check pending approvals in vault."""
    vault_root = Path(os.getenv('VAULT_ROOT', 'My_AI_Employee/AI_Employee_Vault'))
    pending_dir = vault_root / 'Pending_Approval'

    if not pending_dir.exists():
        print("No pending approvals folder found.")
        return

    pending_files = list(pending_dir.glob('*.md'))

    if not pending_files:
        print("✅ No pending approvals!")
        return

    print("\n" + "=" * 70)
    print(f"PENDING APPROVALS ({len(pending_files)} items)")
    print("=" * 70 + "\n")

    for file_path in sorted(pending_files):
        # Extract frontmatter
        with open(file_path, 'r') as f:
            content = f.read()
            if '---' in content:
                parts = content.split('---')
                frontmatter = parts[1] if len(parts) > 1 else ''
                body = parts[2] if len(parts) > 2 else ''
            else:
                frontmatter = ''
                body = content

        # Parse YAML frontmatter
        priority = 'MEDIUM'
        created_at = 'unknown'
        action_type = 'unknown'

        for line in frontmatter.split('\n'):
            if line.startswith('priority:'):
                priority = line.split(':', 1)[1].strip()
            elif line.startswith('created_at:'):
                created_at = line.split(':', 1)[1].strip()
            elif line.startswith('action_type:'):
                action_type = line.split(':', 1)[1].strip()

        # Get title from body
        title_line = [l for l in body.split('\n') if l.startswith('#')]
        title = title_line[0].replace('# ', '').replace('# Approval Request: ', '') if title_line else file_path.stem

        # Calculate age
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now(created.tzinfo) - created
            age_str = f"{age.seconds // 60} min ago" if age.seconds < 3600 else f"{age.days}d {age.seconds // 3600}h ago"
        except:
            age_str = 'unknown'

        # Priority icon
        priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority.lower(), '⚪')

        print(f"{priority_icon} {title}")
        print(f"   Type: {action_type} | Priority: {priority} | Age: {age_str}")
        print(f"   File: {file_path.name}")
        print()

    print("=" * 70)
    print(f"Total pending: {len(pending_files)}")
    print("\nTo approve: Edit file, change status to 'approved', move to Approved/ folder")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    check_pending_approvals()
